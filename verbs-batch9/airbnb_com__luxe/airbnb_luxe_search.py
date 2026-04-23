"""
Playwright script (Python) — Airbnb Luxe Search
Browse luxury stays in a location and extract property details.
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
class AirbnbLuxeSearchRequest:
    location: str = "Malibu, California"
    max_results: int = 5


@dataclass
class LuxePropertyItem:
    property_name: str = ""
    price: str = ""
    bedrooms: str = ""
    rating: str = ""


@dataclass
class AirbnbLuxeSearchResult:
    location: str = ""
    items: List[LuxePropertyItem] = field(default_factory=list)


# Browses Airbnb Luxe listings in a location and extracts property details.
def search_airbnb_luxe(page: Page, request: AirbnbLuxeSearchRequest) -> AirbnbLuxeSearchResult:
    """Search Airbnb Luxe for luxury property listings."""
    encoded = quote_plus(request.location)
    url = f"https://www.airbnb.com/s/{encoded}/homes?refinement_paths%5B%5D=%2Fluxe"
    print(f"Loading {url}...")
    checkpoint("Navigate to Airbnb Luxe")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = AirbnbLuxeSearchResult(location=request.location)

    checkpoint("Extract luxury listings")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('[itemprop="itemListElement"], [data-testid="card-container"], [class*="listing"], [id^="listing_"]');
        for (const card of cards) {
            if (items.length >= max) break;
            const text = (card.textContent || '').replace(/\\s+/g, ' ').trim();

            let name = '';
            const nameEl = card.querySelector('[data-testid="listing-card-title"], [id*="title"], span[class*="title"]');
            if (nameEl) name = nameEl.textContent.trim();
            if (!name) {
                const h = card.querySelector('h3, h2');
                if (h) name = h.textContent.trim();
            }

            let price = '';
            const innerLines = (card.innerText || '').split('\\n').map(l => l.trim());
            for (const line of innerLines) {
                const pm2 = line.match(/^\\$(\\d[\\d,]+)$/);
                if (pm2) { price = '$' + pm2[1]; break; }
            }

            let bedrooms = '';
            const brm = text.match(/(\\d+)\\s*bed(?:room)?s?/i);
            if (brm) bedrooms = brm[1];

            let rating = '';
            const rm = text.match(/(\\d\\.\\d+)\\s*(?:\\(|star|rating|out of)/i);
            if (rm) rating = rm[1];
            if (!rating) {
                const rm2 = text.match(/★\\s*(\\d\\.\\d+)/);
                if (rm2) rating = rm2[1];
            }

            if (name) items.push({property_name: name, price, bedrooms, rating});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = LuxePropertyItem()
        item.property_name = d.get("property_name", "")
        item.price = d.get("price", "")
        item.bedrooms = d.get("bedrooms", "")
        item.rating = d.get("rating", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} luxury properties in '{request.location}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.property_name}")
        print(f"     Price:    {item.price}")
        print(f"     Bedrooms: {item.bedrooms}")
        print(f"     Rating:   {item.rating}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("airbnb_luxe")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_airbnb_luxe(page, AirbnbLuxeSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} listings")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
