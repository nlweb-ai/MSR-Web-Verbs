import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class CareBabysittersRequest:
    location: str = "Austin, TX"
    max_results: int = 5

@dataclass(frozen=True)
class CaregiverProfile:
    name: str = ""
    years_of_experience: str = ""
    hourly_rate: str = ""
    rating_or_reviews: str = ""

@dataclass(frozen=True)
class CareBabysittersResult:
    profiles: list = None  # list[CaregiverProfile]

# Search for babysitters on Care.com in a given location and extract caregiver
# profiles including name, years of experience, hourly rate, and rating/reviews.
def care_babysitters(page: Page, request: CareBabysittersRequest) -> CareBabysittersResult:
    location = request.location
    max_results = request.max_results
    print(f"  Location: {location}")
    print(f"  Max profiles to extract: {max_results}\n")

    # Build direct URL: "Austin, TX" -> "austin-tx"
    slug = re.sub(r'[,.]', '', location).strip().lower().replace(' ', '-')
    url = f"https://www.care.com/babysitters/{slug}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to babysitter search for '{location}'")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    results = []

    # Each profile card has multiple a[href*="/p/"] links with the same href.
    # First, build a map of href → link indices that have name text.
    profile_links = page.locator('a[href*="/p/"]')
    link_count = profile_links.count()
    print(f"  Found {link_count} profile links")

    # Find name links: links where inner_text looks like a person name
    seen_hrefs = set()
    card_texts = []
    for i in range(link_count):
        el = profile_links.nth(i)
        href = el.get_attribute("href") or ""
        if not href or href in seen_hrefs:
            continue
        txt = el.inner_text(timeout=2000).strip()
        # Skip empty, "See profile", etc. - look for name-like text
        if not txt or len(txt) < 2 or "see" in txt.lower() or "profile" in txt.lower():
            continue
        seen_hrefs.add(href)
        # This link has the person's name - go up to find full card text
        card_text = el.evaluate('''el => {
            let p = el;
            for (let i = 0; i < 5; i++) { if (p.parentElement) p = p.parentElement; }
            return p.innerText;
        }''')
        if card_text and len(card_text) > 20:
            card_texts.append(card_text)

    # Further deduplicate by first line (name)
    seen_names = set()
    unique_cards = []
    for card_text in card_texts:
        first_line = card_text.split('\n')[0].strip()
        if first_line and first_line not in seen_names:
            seen_names.add(first_line)
            unique_cards.append(card_text)

    print(f"  Found {len(unique_cards)} unique profile cards")

    for card_text in unique_cards[:max_results]:
        lines = [l.strip() for l in card_text.split("\n") if l.strip()]

        name = "N/A"
        years_of_experience = "N/A"
        hourly_rate = "N/A"
        rating = ""
        review_count = ""

        for line in lines:
            # Hourly rate: "$15/hr"
            rm = re.search(r'\$\d+(?:/hr)?', line)
            if rm and hourly_rate == "N/A":
                hourly_rate = rm.group(0)
                continue
            # Years of experience: "10 years experience"
            em = re.search(r'(\d+)\s*(?:\+\s*)?years?\s*experience', line, re.I)
            if em and years_of_experience == "N/A":
                years_of_experience = em.group(0)
                continue
            # Rating: standalone decimal like "4.6"
            if re.match(r'^\d\.\d$', line) and not rating:
                rating = line
                continue
            # Review count: "(1)" or "(23)"
            rm2 = re.match(r'^\((\d+)\)$', line)
            if rm2 and not review_count:
                review_count = rm2.group(1)
                continue
            # Name: short text like "Chelsea W." - first proper name-like line
            if (name == "N/A"
                    and 2 <= len(line) <= 30
                    and re.match(r'^[A-Z][a-z]+', line)
                    and not re.search(r'(experience|hire|filter|mile|hour|rate|from|ago|Austin|See|Meal|Craft)', line, re.I)):
                name = line

        rating_or_reviews = "N/A"
        if rating and review_count:
            rating_or_reviews = f"{rating} ({review_count} reviews)"
        elif rating:
            rating_or_reviews = rating
        elif review_count:
            rating_or_reviews = f"{review_count} reviews"

        if name != "N/A":
            results.append(CaregiverProfile(
                name=name,
                years_of_experience=years_of_experience,
                hourly_rate=hourly_rate,
                rating_or_reviews=rating_or_reviews,
            ))

    print("=" * 60)
    print(f"Care.com – Babysitters in {location}")
    print("=" * 60)
    for idx, p in enumerate(results, 1):
        print(f"\n{idx}. {p.name}")
        print(f"   Experience: {p.years_of_experience}")
        print(f"   Rate: {p.hourly_rate}")
        print(f"   Rating/Reviews: {p.rating_or_reviews}")

    print(f"\nFound {len(results)} caregiver profiles")

    return CareBabysittersResult(profiles=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = care_babysitters(page, CareBabysittersRequest())
        print(f"\nReturned {len(result.profiles or [])} profiles")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
