"""
Playwright script (Python) — Alibaba Wholesale Product Search
Search for products and extract listing details.
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
class AlibabaSearchRequest:
    search_query: str = "LED strip lights"
    max_results: int = 5


@dataclass
class ProductItem:
    product_name: str = ""
    supplier: str = ""
    price_range: str = ""
    min_order_qty: str = ""
    supplier_rating: str = ""


@dataclass
class AlibabaSearchResult:
    query: str = ""
    items: List[ProductItem] = field(default_factory=list)


# Searches Alibaba for wholesale products and extracts listing details.
def search_alibaba(page: Page, request: AlibabaSearchRequest) -> AlibabaSearchResult:
    """Search Alibaba for wholesale products."""
    encoded = quote_plus(request.search_query)
    url = f"https://www.alibaba.com/trade/search?SearchText={encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Alibaba search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = AlibabaSearchResult(query=request.search_query)

    checkpoint("Extract product listings")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('[class*="organic-list"] [class*="list-card"], [class*="card-info"], [class*="J-offer-wrapper"], [class*="organic-gallery-offer"]');
        let candidates = Array.from(cards).filter(c => c.textContent.length > 50);
        candidates = candidates.filter(c => !candidates.some(o => o !== c && o.contains(c)));
        for (const card of candidates) {
            if (items.length >= max) break;
            const text = (card.textContent || '').replace(/\\s+/g, ' ').trim();

            let name = '';
            const nameEl = card.querySelector('h2 a, h3 a, [class*="title"] a, [class*="elements-title-normal"]');
            if (nameEl) name = nameEl.textContent.trim();

            let supplier = '';
            const supEl = card.querySelector('[class*="company"], [class*="supplier"], a[class*="seller"]');
            if (supEl) supplier = supEl.textContent.trim();

            let price = '';
            const priceEl = card.querySelector('[class*="price"], [class*="Price"]');
            if (priceEl) price = priceEl.textContent.trim();
            if (!price) {
                const pm = text.match(/(\\$[\\d.,]+\\s*-\\s*\\$[\\d.,]+|\\$[\\d.,]+)/);
                if (pm) price = pm[1];
            }

            let moq = '';
            let rating = '';
            const lines = card.innerText.split('\\n').map(l => l.trim());
            for (const line of lines) {
                if (!moq) {
                    const mm = line.match(/^Min\\.?\\s*order:?\\s*(.+)/i);
                    if (mm) moq = mm[1].trim();
                }
                if (!rating) {
                    const rm = line.match(/^(\\d\\.\\d)$/);
                    if (rm) rating = rm[1];
                }
            }

            if (name) items.push({product_name: name, supplier, price_range: price, min_order_qty: moq, supplier_rating: rating});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ProductItem()
        item.product_name = d.get("product_name", "")
        item.supplier = d.get("supplier", "")
        item.price_range = d.get("price_range", "")
        item.min_order_qty = d.get("min_order_qty", "")
        item.supplier_rating = d.get("supplier_rating", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} products for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.product_name}")
        print(f"     Supplier: {item.supplier}")
        print(f"     Price:    {item.price_range}")
        print(f"     MOQ:      {item.min_order_qty}")
        print(f"     Rating:   {item.supplier_rating}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("alibaba")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_alibaba(page, AlibabaSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
