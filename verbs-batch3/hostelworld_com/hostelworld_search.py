import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


RATING_RE = re.compile(r'^\d+\.\d$')
RATING_LABELS = {'Superb', 'Fabulous', 'Very Good', 'Good', 'Average'}
PRICE_RE = re.compile(r'^US\$[\d,.]+$')
DIST_RE = re.compile(r'^[\d.]+km from city centre$')


@dataclass(frozen=True)
class HostelSearchRequest:
    city: str
    guests: int
    max_results: int


@dataclass(frozen=True)
class Hostel:
    name: str
    price: str
    rating: str
    distance: str


@dataclass(frozen=True)
class HostelSearchResult:
    hostels: list  # list[Hostel]


# Search for hostels on Hostelworld by city and number of guests.
# Extracts hostel name, price per night, rating, and distance from city center.
def hostelworld_search(page: Page, request: HostelSearchRequest) -> HostelSearchResult:
    print(f"  City: {request.city}")
    print(f"  Guests: {request.guests}\n")

    results = []

    url = f"https://www.hostelworld.com/hostels/{request.city}"
    print(f"Loading {url}...")
    checkpoint("Navigate to page")
    page.goto(url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(10000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Parse hostel listings
    # Pattern: 'Hostel' marker -> name -> rating -> label -> (count) -> distance -> ... -> Dorms From -> price
    i = 0
    while i < len(text_lines) and len(results) < request.max_results:
        line = text_lines[i]
        if line == "Hostel" and i + 1 < len(text_lines):
            name = text_lines[i + 1] if i + 1 < len(text_lines) else ""
            rating = ""
            distance = "N/A"
            price = "N/A"

            # Look forward for rating, distance, price
            for j in range(i + 2, min(i + 20, len(text_lines))):
                jline = text_lines[j]
                if RATING_RE.match(jline) and not rating:
                    label = text_lines[j + 1] if j + 1 < len(text_lines) else ""
                    rating = jline + " " + label if label in RATING_LABELS else jline
                elif DIST_RE.match(jline):
                    distance = jline
                elif jline == "Dorms From" and j + 1 < len(text_lines):
                    price = text_lines[j + 1]
                    break
                elif jline == "Hostel":
                    # reached next listing, take what we have
                    break

            if name:
                results.append(Hostel(
                    name=name,
                    price=price,
                    rating=rating,
                    distance=distance,
                ))
            i += 2
        else:
            i += 1

    print("=" * 60)
    print(f"Hostels in {request.city}")
    print("=" * 60)
    for idx, r in enumerate(results, 1):
        print(f"\n{idx}. {r.name}")
        print(f"   Price/night: {r.price}")
        print(f"   Rating:      {r.rating}")
        print(f"   Distance:    {r.distance}")

    print(f"\nFound {len(results)} hostels")

    return HostelSearchResult(hostels=results)


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    profile_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default",
    )
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            profile_dir,
            headless=False,
            channel="chrome",
        )
        page = context.pages[0] if context.pages else context.new_page()
        request = HostelSearchRequest(
            city="Barcelona",
            guests=2,
            max_results=5,
        )
        result = hostelworld_search(page, request)
        print(f"\nReturned {len(result.hostels)} hostels")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)