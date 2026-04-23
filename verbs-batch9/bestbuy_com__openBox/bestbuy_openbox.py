"""
Playwright script (Python) — Best Buy Open Box
Browse Best Buy open-box deals.
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
class BestBuyOpenBoxRequest:
    category: str = "laptops"
    max_results: int = 5


@dataclass
class OpenBoxItem:
    product_name: str = ""
    open_box_price: str = ""
    original_price: str = ""
    rating: str = ""


@dataclass
class BestBuyOpenBoxResult:
    category: str = ""
    items: List[OpenBoxItem] = field(default_factory=list)


def browse_bestbuy_openbox(page: Page, request: BestBuyOpenBoxRequest) -> BestBuyOpenBoxResult:
    """Browse Best Buy open-box deals."""
    encoded = quote_plus(request.category)
    url = f"https://www.bestbuy.com/site/searchpage.jsp?st={encoded}&qp=condition_facet%3DCondition~Open-Box"
    print(f"Loading {url}...")
    checkpoint("Navigate to open-box listings")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = BestBuyOpenBoxResult(category=request.category)

    checkpoint("Extract open-box items")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();
        const cards = document.querySelectorAll('li.product-list-item, li[class*="product-list-item"], .sku-item');
        for (const card of cards) {
            if (items.length >= max) break;
            const lines = card.innerText.split('\\n').map(l => l.trim()).filter(l => l);
            if (lines.length < 3) continue;

            const name = lines[0];
            if (!name || name.length < 10 || seen.has(name)) continue;
            seen.add(name
            let obPrice = '';
            let origPrice = '';
            const prices = [];
            for (const line of lines) {
                const pm = line.match(/^(\\$[\\d,]+(?:\\.\\d{2})?)$/);
                if (pm) prices.push(pm[1]);
            }
            if (prices.length >= 1) obPrice = prices[0];
            if (prices.length >= 2) origPrice = prices[1];

            let rating = '';
            for (const line of lines) {
                const rm = line.match(/^(\\d\\.\\d)$/);
                if (rm) { rating = rm[1]; break; }
            }

            items.push({product_name: name, open_box_price: obPrice, original_price: origPrice, rating: rating});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = OpenBoxItem()
        item.product_name = d.get("product_name", "")
        item.open_box_price = d.get("open_box_price", "")
        item.original_price = d.get("original_price", "")
        item.rating = d.get("rating", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} open-box items in '{request.category}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.product_name[:80]}")
        print(f"     OB Price: {item.open_box_price}  Original: {item.original_price}  Rating: {item.rating}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("bestbuy_ob")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = browse_bestbuy_openbox(page, BestBuyOpenBoxRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} items")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
