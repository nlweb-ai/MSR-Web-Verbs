"""
Petfinder - Adoptable Pet Search
Search for adoptable pets near a ZIP code and extract pet listings.
"""

import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


MILES_RE = re.compile(r'^\d+ miles? away$')
AGE_GENDER_RE = re.compile(r'^(\w+)\s*[\u2022]\s*(\w+)$')


@dataclass(frozen=True)
class PetfinderSearchRequest:
    animal_type: str = "dogs"
    location: str = "90210"
    max_results: int = 5


@dataclass(frozen=True)
class PetListing:
    name: str = ""
    breed: str = ""
    age: str = ""
    gender: str = ""
    shelter: str = ""


@dataclass(frozen=True)
class PetfinderSearchResult:
    pets: tuple = ()


# Search for adoptable pets on petfinder.com by animal type and ZIP code,
# then extract pet listings with name, breed, age, gender, and shelter name.
def petfinder_search(page: Page, request: PetfinderSearchRequest) -> PetfinderSearchResult:
    url = f"https://www.petfinder.com/search/{request.animal_type}-for-adoption/us/?location={request.location}"
    print(f"  URL: {url}\n")

    checkpoint("Navigating to Petfinder search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    results = []

    # Skip to 'pet results'
    i = 0
    while i < len(text_lines):
        if text_lines[i] == 'pet results':
            i += 1
            break
        i += 1

    while i < len(text_lines) and len(results) < request.max_results:
        line = text_lines[i]

        # Detect 'X miles away' → pet entry
        if MILES_RE.match(line):
            name = text_lines[i - 1] if i > 0 else 'Unknown'
            age_gender_line = text_lines[i + 1] if i + 1 < len(text_lines) else ''
            breed = text_lines[i + 2] if i + 2 < len(text_lines) else 'Unknown'

            # Parse age and gender from 'Adult • Male'
            ag = AGE_GENDER_RE.match(age_gender_line)
            age = ag.group(1) if ag else 'Unknown'
            gender = ag.group(2) if ag else 'Unknown'

            # Find shelter name
            shelter = 'Unknown'
            for j in range(i + 3, min(i + 20, len(text_lines))):
                if text_lines[j] == 'Shelter':
                    shelter = text_lines[j + 1] if j + 1 < len(text_lines) else 'Unknown'
                    break

            results.append(PetListing(
                name=name,
                breed=breed,
                age=age,
                gender=gender,
                shelter=shelter,
            ))

        i += 1

    print("=" * 60)
    print(f"Adoptable {request.animal_type.title()} near {request.location}")
    print("=" * 60)
    for idx, r in enumerate(results, 1):
        print(f"\n{idx}. {r.name}")
        print(f"   Breed:   {r.breed}")
        print(f"   Age:     {r.age}")
        print(f"   Gender:  {r.gender}")
        print(f"   Shelter: {r.shelter}")

    print(f"\nFound {len(results)} pets")

    return PetfinderSearchResult(pets=tuple(results))


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_user_data = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            chrome_user_data,
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        result = petfinder_search(page, PetfinderSearchRequest())
        print(f"\nReturned {len(result.pets)} pets")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)