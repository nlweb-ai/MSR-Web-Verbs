"""
Auto-generated Playwright script (Python)
Amazon Warehouse – Search warehouse deals
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
class WarehouseDealRequest:
    category: str = "electronics"
    max_results: int = 5


@dataclass
class WarehouseDealItem:
    product_name: str = ""
    original_price: str = ""
    warehouse_price: str = ""
    condition: str = ""
    discount_percentage: str = ""


@dataclass
class WarehouseDealResult:
    items: List[WarehouseDealItem] = field(default_factory=list)


# Search Amazon Warehouse deals for a given category and extract deal listings.
def amazon_warehouse_search(page: Page, request: WarehouseDealRequest) -> WarehouseDealResult:
    """Search Amazon Warehouse deals by category."""
    print(f"  Category: {request.category}\n")

    encoded = quote_plus(request.category)
    url = f"https://www.amazon.com/s?k={encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Amazon search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = WarehouseDealResult()

    checkpoint("Extract warehouse deal listings")
    js_code = """(max) => {
        const cards = document.querySelectorAll('[data-component-type="s-search-result"]');
        const items = [];
        for (const card of cards) {
            if (items.length >= max) break;
            const titleEl = card.querySelector('h2 a span, [data-cy="title-recipe"] span');
            const priceWholeEl = card.querySelector('.a-price .a-price-whole');
            const priceFractionEl = card.querySelector('.a-price .a-price-fraction');
            const origPriceEl = card.querySelector('.a-price.a-text-price .a-offscreen, [data-a-strike="true"] .a-offscreen');
            const conditionEl = card.querySelector('.a-color-secondary .a-size-base, [aria-label*="condition"]');

            const productName = titleEl ? titleEl.textContent.trim() : '';
            let warehousePrice = '';
            if (priceWholeEl) {
                warehousePrice = '$' + priceWholeEl.textContent.trim() + (priceFractionEl ? priceFractionEl.textContent.trim() : '00');
            }
            const originalPrice = origPriceEl ? origPriceEl.textContent.trim() : '';

            let condition = '';
            const text = card.innerText;
            const condMatch = text.match(/(Used\\s*-\\s*[\\w\\s]+|Renewed|Refurbished|Open Box)/i);
            if (condMatch) condition = condMatch[1].trim();

            let discount = '';
            const discMatch = text.match(/(\\d+)%\\s*off/i);
            if (discMatch) discount = discMatch[1] + '%';

            if (productName) {
                items.push({product_name: productName, original_price: originalPrice, warehouse_price: warehousePrice, condition, discount_percentage: discount});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = WarehouseDealItem()
        item.product_name = d.get("product_name", "")
        item.original_price = d.get("original_price", "")
        item.warehouse_price = d.get("warehouse_price", "")
        item.condition = d.get("condition", "")
        item.discount_percentage = d.get("discount_percentage", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Deal {i}:")
        print(f"    Product:    {item.product_name}")
        print(f"    Original:   {item.original_price}")
        print(f"    Warehouse:  {item.warehouse_price}")
        print(f"    Condition:  {item.condition}")
        print(f"    Discount:   {item.discount_percentage}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("amazon_warehouse")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = WarehouseDealRequest()
            result = amazon_warehouse_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} deals")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
