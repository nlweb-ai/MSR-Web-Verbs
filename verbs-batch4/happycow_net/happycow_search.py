import re
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class HappyCowSearchRequest:
    location: str = "Portland, OR"
    max_results: int = 5

@dataclass(frozen=True)
class HappyCowRestaurant:
    name: str = ""
    cuisine_type: str = ""
    rating: str = ""
    address: str = ""
    price_range: str = ""

@dataclass(frozen=True)
class HappyCowSearchResult:
    restaurants: list = None  # list[HappyCowRestaurant]

# Search for vegan/vegetarian restaurants on HappyCow in a given location
# and extract name, cuisine type, rating, address, and price range.
def happycow_search(page: Page, request: HappyCowSearchRequest) -> HappyCowSearchResult:
    location = request.location
    max_results = request.max_results
    print(f"  Location: {location}")
    print(f"  Max results: {max_results}\n")

    url = f"https://www.happycow.net/searchmap?s=3&location={quote_plus(location)}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to HappyCow search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""

    results = []

    # Try structured extraction via restaurant listing elements
    cards = page.locator(
        '[class*="venue-card"], '
        '[class*="VenueCard"], '
        '[class*="restaurant-card"], '
        '[class*="listing"], '
        'a[href*="/reviews/"]'
    )
    count = cards.count()
    print(f"  Found {count} restaurant cards via selectors")

    if count > 0:
        for i in range(min(count, max_results)):
            card = cards.nth(i)
            try:
                card_text = card.inner_text(timeout=3000).strip()
                lines = [l.strip() for l in card_text.split("\n") if l.strip()]

                name = "N/A"
                cuisine_type = "N/A"
                rating = "N/A"
                address = "N/A"
                price_range = "N/A"

                for line in lines:
                    # Rating pattern (e.g. "4.5" or "4.5/5")
                    rm = re.match(r'^(\d+(?:\.\d+)?)\s*(?:/\s*5)?$', line)
                    if rm and rating == "N/A":
                        rating = rm.group(1)
                        continue
                    # Cuisine type keywords
                    low = line.lower()
                    if cuisine_type == "N/A" and any(
                        kw in low for kw in ["vegan", "vegetarian", "veg-friendly", "veg friendly"]
                    ):
                        cuisine_type = line
                        continue
                    # Price range ($ symbols or "cheap"/"moderate"/"expensive")
                    if re.match(r'^[\$€£]{1,4}$', line):
                        price_range = line
                        continue
                    if re.match(r'^(cheap|moderate|expensive|budget|pricey)$', low):
                        price_range = line
                        continue
                    # Address-like line (contains numbers + street words)
                    if re.search(r'\d+.*(?:st|ave|rd|blvd|dr|ln|way|street|avenue|road|hwy|pkwy)', low):
                        if address == "N/A":
                            address = line
                            continue
                    # Name — first substantial non-matched line
                    if name == "N/A" and len(line) > 2 and not re.match(r'^[\d,.$/€£%]+$', line):
                        name = line
                        continue

                if name != "N/A":
                    results.append(HappyCowRestaurant(
                        name=name,
                        cuisine_type=cuisine_type,
                        rating=rating,
                        address=address,
                        price_range=price_range,
                    ))
            except Exception:
                continue

    # Fallback: text-based extraction
    if not results:
        print("  Card selectors missed, trying text-based extraction...")
        text_lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        i = 0
        while i < len(text_lines) and len(results) < max_results:
            line = text_lines[i]
            low = line.lower()

            # Look for lines that could be restaurant names (descriptive text, not purely numeric)
            if len(line) > 3 and not re.match(r'^[\d,.$/€£%]+$', line):
                name = line
                cuisine_type = "N/A"
                rating = "N/A"
                address = "N/A"
                price_range = "N/A"

                # Scan nearby lines for details
                for j in range(i + 1, min(len(text_lines), i + 8)):
                    nearby = text_lines[j]
                    nearby_low = nearby.lower()

                    # Rating
                    rm = re.match(r'^(\d+(?:\.\d+)?)\s*(?:/\s*5)?$', nearby)
                    if rm and rating == "N/A":
                        rating = rm.group(1)
                        continue
                    # Cuisine type
                    if cuisine_type == "N/A" and any(
                        kw in nearby_low for kw in ["vegan", "vegetarian", "veg-friendly", "veg friendly"]
                    ):
                        cuisine_type = nearby
                        continue
                    # Price
                    if re.match(r'^[\$€£]{1,4}$', nearby):
                        price_range = nearby
                        continue
                    # Address
                    if re.search(r'\d+.*(?:st|ave|rd|blvd|dr|ln|way|street|avenue|road|hwy|pkwy)', nearby_low):
                        if address == "N/A":
                            address = nearby
                            continue

                if name != "N/A" and (cuisine_type != "N/A" or rating != "N/A"):
                    results.append(HappyCowRestaurant(
                        name=name,
                        cuisine_type=cuisine_type,
                        rating=rating,
                        address=address,
                        price_range=price_range,
                    ))
                    i += 7
                    continue
            i += 1

        results = results[:max_results]

    print("=" * 60)
    print(f"HappyCow - Restaurant Results for \"{location}\"")
    print("=" * 60)
    for idx, r in enumerate(results, 1):
        print(f"\n{idx}. {r.name}")
        print(f"   Cuisine Type: {r.cuisine_type}")
        print(f"   Rating: {r.rating}")
        print(f"   Address: {r.address}")
        print(f"   Price Range: {r.price_range}")

    print(f"\nFound {len(results)} restaurants")

    return HappyCowSearchResult(restaurants=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = happycow_search(page, HappyCowSearchRequest())
        print(f"\nReturned {len(result.restaurants or [])} restaurants")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
