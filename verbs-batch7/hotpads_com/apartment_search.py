"""
Auto-generated Playwright script (Python)
HotPads – Search apartments for rent

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re, urllib.parse
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ApartmentSearchRequest:
    city: str = "Chicago, IL"
    max_price: int = 2000
    max_results: int = 5


@dataclass
class Apartment:
    name: str = ""
    price: str = ""
    bedrooms: str = ""
    location: str = ""
    building_type: str = ""


@dataclass
class ApartmentSearchResult:
    apartments: List[Apartment] = field(default_factory=list)


def apartment_search(page: Page, request: ApartmentSearchRequest) -> ApartmentSearchResult:
    """Search HotPads for apartments and extract listings."""
    print(f"  City: {request.city}")
    print(f"  Max Price: ${request.max_price}")
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Navigate to HotPads search")
    slug = re.sub(r"[^a-z0-9-]", "", re.sub(r",?\s+", "-", request.city.lower()))
    url = f"https://hotpads.com/{slug}/apartments-for-rent?maxPrice={request.max_price}"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    checkpoint("Extract apartment listings")
    result = ApartmentSearchResult()

    items = page.evaluate(
        r"""(max) => {
            const cards = document.querySelectorAll('article[data-name="ListingCardContainer"]');
            const results = [];
            for (let i = 0; i < cards.length && results.length < max; i++) {
                const card = cards[i];

                const priceEl = card.querySelector('[data-name="PriceText"]');
                const nameEl = card.querySelector('[data-name="ListingCardAnchor"]');
                const infoEl = card.querySelector('[data-name="DetailedInfoText"]');

                const price = priceEl ? priceEl.textContent.replace(/Total price/i, '').trim() : '';
                const name = nameEl ? nameEl.textContent.trim() : '';

                let bedrooms = '';
                let buildingType = '';
                let location = '';

                if (infoEl) {
                    const infoText = infoEl.textContent;
                    // Beds: "Studio - 2 beds" or "1 - 3 beds" or "2 beds, 2 baths"
                    // Strip price portion first to avoid "$5,1003 - 4 beds" concatenation
                    const stripped = infoText.replace(/\$[\d,.]+(k)?\s*-\s*\$[\d,.]+(k)?(\s*Total price)?/g, '');
                    const bedsMatch = stripped.match(/(Studio(?:\s*-\s*\d+\s*beds?)?|\d+(?:\s*-\s*\d+)?\s*beds?(?:,\s*\d+\s*baths?)?)/i);
                    bedrooms = bedsMatch ? bedsMatch[1].trim() : '';

                    // Building type: "Apt building" or similar before "in City, ST"
                    const typeMatch = infoText.match(/(Apt building|Condo|House|Townhouse|Room)\s+in\s+/i);
                    buildingType = typeMatch ? typeMatch[1] : '';

                    // Location: "in City, ST"
                    const locMatch = infoText.match(/in\s+([A-Z][a-zA-Z\s]+,\s*[A-Z]{2})/);
                    location = locMatch ? locMatch[1] : '';
                }

                if (name) {
                    results.push({name, price, bedrooms, location, building_type: buildingType});
                }
            }
            return results;
        }""",
        request.max_results,
    )

    for item in items:
        a = Apartment()
        a.name = item.get("name", "")
        a.price = item.get("price", "")
        a.bedrooms = item.get("bedrooms", "")
        a.location = item.get("location", "")
        a.building_type = item.get("building_type", "")
        result.apartments.append(a)

    for i, a in enumerate(result.apartments):
        print(f"  Apartment {i + 1}:")
        print(f"    Name:     {a.name}")
        print(f"    Price:    {a.price}")
        print(f"    Beds:     {a.bedrooms}")
        print(f"    Type:     {a.building_type}")
        print(f"    Location: {a.location}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("hotpads")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = ApartmentSearchRequest()
            result = apartment_search(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.apartments)} apartments")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
