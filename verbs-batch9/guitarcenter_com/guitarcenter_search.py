"""
Playwright script (Python) — Guitar Center Search
Search Guitar Center for musical instruments.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GuitarCenterRequest:
    search_query: str = "acoustic guitars"
    max_results: int = 5


@dataclass
class GuitarItem:
    name: str = ""
    brand: str = ""
    price: str = ""
    body_type: str = ""
    rating: str = ""


@dataclass
class GuitarCenterResult:
    query: str = ""
    items: List[GuitarItem] = field(default_factory=list)


# Searches Guitar Center for products matching the query and returns
# up to max_results items with name, brand, price, body type, and rating.
def search_guitarcenter(page: Page, request: GuitarCenterRequest) -> GuitarCenterResult:
    import urllib.parse
    url = f"https://www.guitarcenter.com/search?typeAheadSuggestion=false&fromRecentHistory=false&Ntt={urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = GuitarCenterResult(query=request.search_query)

    checkpoint("Extract product listings")
    js_code = """(max) => {
        const results = [];
        const cards = document.querySelectorAll('.plp-product-details, [data-product-name], [class*="product-card"], [data-product-id]');
        for (const card of cards) {
            if (results.length >= max) break;
            const text = card.innerText || '';
            const lines = text.split('\\n').map(l => l.trim()).filter(l => l);

            // Name: from data attribute or first substantial text line
            let name = card.getAttribute('data-product-name') || '';
            if (!name) {
                const nameEl = card.querySelector('a');
                if (nameEl) name = nameEl.innerText.trim();
            }
            if (!name) name = lines.find(l => l.length > 10 && !l.startsWith('$')) || '';
            if (!name || name.length < 5) continue;
            if (results.some(r => r.name === name)) continue;

            let brand = '';
            const brandMatch = name.match(/^(\\S+)/);
            if (brandMatch) brand = brandMatch[1];

            let price = '';
            const priceMatch = text.match(/\\$[\\d,.]+/);
            if (priceMatch) price = priceMatch[0];

            let bodyType = '';
            const bodyMatch = text.match(/(dreadnought|concert|parlor|jumbo|grand auditorium|orchestra|cutaway|classical)/i);
            if (bodyMatch) bodyType = bodyMatch[1];

            let rating = '';
            const ratingEl = card.querySelector('[class*="rating"], [class*="star"], [aria-label*="star"]');
            if (ratingEl) {
                const ariaLabel = ratingEl.getAttribute('aria-label') || '';
                const rateMatch = ariaLabel.match(/([\d.]+)/);
                if (rateMatch) rating = rateMatch[1];
                if (!rating) rating = ratingEl.textContent.trim();
            }

            results.push({ name, brand, price, body_type: bodyType, rating });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = GuitarItem()
        item.name = d.get("name", "")
        item.brand = d.get("brand", "")
        item.price = d.get("price", "")
        item.body_type = d.get("body_type", "")
        item.rating = d.get("rating", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} products for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name}")
        print(f"     Brand: {item.brand}  Price: {item.price}")
        print(f"     Body: {item.body_type}  Rating: {item.rating}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("guitarcenter")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_guitarcenter(page, GuitarCenterRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
