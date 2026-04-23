"""
Playwright script (Python) — ApartmentList Search
Search for apartments on ApartmentList.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ApartmentListSearchRequest:
    location: str = "Seattle, WA"
    max_results: int = 5


@dataclass
class ApartmentItem:
    property_name: str = ""
    rent_range: str = ""
    bedrooms: str = ""
    rating: str = ""


@dataclass
class ApartmentListSearchResult:
    location: str = ""
    items: List[ApartmentItem] = field(default_factory=list)


def search_apartmentlist(page: Page, request: ApartmentListSearchRequest) -> ApartmentListSearchResult:
    """Search ApartmentList for apartments."""
    # Convert "Seattle, WA" -> /wa/seattle
    parts = request.location.split(",")
    city = parts[0].strip().lower().replace(" ", "-")
    state = parts[1].strip().lower() if len(parts) > 1 else ""
    url = f"https://www.apartmentlist.com/{state}/{city}"
    print(f"Loading {url}...")
    checkpoint("Navigate to listings")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = ApartmentListSearchResult(location=request.location)

    checkpoint("Extract apartments")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('[data-testid*="listing"], [class*="ListingCard"], [class*="listing-card"], article, .property-card');
        for (const card of cards) {
            if (items.length >= max) break;
            const lines = card.innerText.split('\\n').map(l => l.trim()).filter(l => l);

            let name = '';
            const nameEl = card.querySelector('h2, h3, [class*="name"], [class*="Name"], [data-testid*="name"]');
            if (nameEl) name = nameEl.textContent.trim();
            if (!name || name.length < 3) continue;

            let rent = '';
            for (const line of lines) {
                const rm = line.match(/^(\\$[\\d,]+(?:\\s*[-\\u2013]\\s*\\$[\\d,]+)?)$/);
                if (rm) { rent = rm[1]; break; }
            }

            let beds = '';
            for (const line of lines) {
                const bm = line.match(/(\\d+)\\s*bed/i);
                if (bm) { beds = bm[0]; break; }
                if (line.match(/^Studio$/i)) { beds = 'Studio'; break; }
            }

            let rating = '';
            for (const line of lines) {
                const rtm = line.match(/^(\\d+\\.\\d+)$/);
                if (rtm) { rating = rtm[1]; break; }
            }

            items.push({property_name: name, rent_range: rent, bedrooms: beds, rating: rating});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ApartmentItem()
        item.property_name = d.get("property_name", "")
        item.rent_range = d.get("rent_range", "")
        item.bedrooms = d.get("bedrooms", "")
        item.rating = d.get("rating", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} apartments in '{request.location}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.property_name}")
        print(f"     Rent: {item.rent_range}  Beds: {item.bedrooms}  Rating: {item.rating}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("apartmentlist")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_apartmentlist(page, ApartmentListSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} apartments")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
