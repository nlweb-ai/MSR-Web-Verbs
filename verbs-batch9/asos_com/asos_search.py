"""
Playwright script (Python) — ASOS Search
Search for products on ASOS.
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
class AsosSearchRequest:
    query: str = "women's dresses"
    max_price: int = 50
    max_results: int = 5


@dataclass
class AsosProductItem:
    product_name: str = ""
    brand: str = ""
    price: str = ""
    sizes: str = ""
    colors: str = ""


@dataclass
class AsosSearchResult:
    query: str = ""
    items: List[AsosProductItem] = field(default_factory=list)


def search_asos(page: Page, request: AsosSearchRequest) -> AsosSearchResult:
    """Search ASOS for products."""
    encoded = quote_plus(request.query)
    url = f"https://www.asos.com/us/search/?q={encoded}&priceMax={request.max_price}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = AsosSearchResult(query=request.query)

    checkpoint("Extract products")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('li[class*="productTile"]');
        for (const card of cards) {
            if (items.length >= max) break;
            const link = card.querySelector('a[class*="productLink"]');
            if (!link) continue;

            const label = link.getAttribute('aria-label') || '';
            // aria-label format: "Product Name, Price $XX.XX"
            let name = '';
            let price = '';
            const priceMatch = label.match(/,\\s*Price\\s*(\\$[\\d,.]+(?:\\s*-\\s*\\$[\\d,.]+)?)/i);
            if (priceMatch) {
                name = label.substring(0, label.indexOf(priceMatch[0])).trim();
                price = priceMatch[1];
            } else {
                name = label;
            }
            if (!name) continue;

            // Try to extract brand from name (first word before space)
            let brand = '';
            const brandPatterns = ['ASOS DESIGN', 'Topshop', 'COLLUSION', 'Reclaimed Vintage', 'Pull&Bear', 'Stradivarius', 'Monki', 'Weekday', 'New Look', 'River Island', 'Miss Selfridge'];
            for (const bp of brandPatterns) {
                if (name.startsWith(bp)) { brand = bp; break; }
            }

            items.push({product_name: name, brand: brand, price: price, sizes: '', colors: ''});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = AsosProductItem()
        item.product_name = d.get("product_name", "")
        item.brand = d.get("brand", "")
        item.price = d.get("price", "")
        item.sizes = d.get("sizes", "")
        item.colors = d.get("colors", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} products for '{request.query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.product_name[:80]}")
        print(f"     Brand: {item.brand}  Price: {item.price}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("asos")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_asos(page, AsosSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
