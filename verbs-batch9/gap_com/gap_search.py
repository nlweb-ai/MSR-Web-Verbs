"""
Playwright script (Python) — Gap Product Search
Search for products on Gap.com.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GapSearchRequest:
    search_query: str = "men's jeans"
    max_results: int = 5


@dataclass
class ProductItem:
    name: str = ""
    original_price: str = ""
    sale_price: str = ""
    discount: str = ""


@dataclass
class GapSearchResult:
    query: str = ""
    items: List[ProductItem] = field(default_factory=list)


# Searches Gap.com for products matching the query and returns
# up to max_results products with name, style, price, colors, and sizes.
def search_gap_products(page: Page, request: GapSearchRequest) -> GapSearchResult:
    import urllib.parse
    url = f"https://www.gap.com/browse/search.do?searchText={urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = GapSearchResult(query=request.search_query)

    checkpoint("Extract product listings")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        const cards = document.querySelectorAll('[class*="product-card"]');
        for (const card of cards) {
            if (results.length >= max) break;
            const lines = card.innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 3 || lines.length > 10) continue;
            // Find the product name (not a badge, not a price, not "+N")
            let name = '', price = '', discount = '';
            for (const l of lines) {
                const t = l.trim();
                if (t.startsWith('$')) { price = t; continue; }
                if (t.match(/^\\+\\d+$/) || t.match(/^\\d+ colors?$/)) continue;
                if (t.match(/off:|limited time/i)) { discount = t; continue; }
                if (t === 'Best seller' || t === 'New') continue;
                if (!name && t.length > 3) name = t;
            }
            if (!name || seen.has(name)) continue;
            seen.add(name);
            // Parse price: "$69.95$41.00" -> original=$69.95, sale=$41.00
            let original_price = '', sale_price = '';
            const priceMatch = price.match(/^(\\$[\\d.]+)(\\$[\\d.]+)$/);
            if (priceMatch) {
                original_price = priceMatch[1];
                sale_price = priceMatch[2];
            } else {
                sale_price = price;
            }
            results.push({name, original_price, sale_price, discount});
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ProductItem()
        item.name = d.get("name", "")
        item.original_price = d.get("original_price", "")
        item.sale_price = d.get("sale_price", "")
        item.discount = d.get("discount", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} products for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name}")
        print(f"     Price: {item.sale_price}  Was: {item.original_price}  {item.discount}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("gap")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_gap_products(page, GapSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
