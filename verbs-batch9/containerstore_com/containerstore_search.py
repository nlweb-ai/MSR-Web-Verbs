"""
Playwright script (Python) — Container Store Search
Search for products on The Container Store.
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
class ContainerStoreSearchRequest:
    query: str = "closet organization"
    max_results: int = 5


@dataclass
class ProductItem:
    name: str = ""
    price: str = ""
    original_price: str = ""
    review_count: str = ""


@dataclass
class ContainerStoreSearchResult:
    query: str = ""
    items: List[ProductItem] = field(default_factory=list)


def search_containerstore(page: Page, request: ContainerStoreSearchRequest) -> ContainerStoreSearchResult:
    """Search The Container Store for products."""
    encoded = quote_plus(request.query)
    url = f"https://www.containerstore.com/s?q={encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = ContainerStoreSearchResult(query=request.query)

    checkpoint("Extract products")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('.MuiGrid-grid-sm-4');
        for (const card of cards) {
            if (items.length >= max) break;
            const lines = card.innerText.split('\\n').map(l => l.trim()).filter(l => l);
            if (lines.length < 3) continue;

            let price = '';
            let originalPrice = '';
            let name = '';
            let reviewCount = '';
            for (const line of lines) {
                if (!price && line.startsWith('$')) { price = line; continue; }
                if (line.startsWith('Was ')) { originalPrice = line.replace('Was ', ''); continue; }
                if (line.match(/^\\d+$/) && !reviewCount) { reviewCount = line; continue; }
                if (!name && !line.startsWith('$') && line.length >= 5
                    && !line.match(/^(CHOOSE|ADD|SHOP|VIEW|\\+)/i)) {
                    name = line;
                }
            }
            if (!name || name.length < 3) continue;
            if (items.some(i => i.name === name)) continue;
            items.push({name, price, original_price: originalPrice, review_count: reviewCount});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ProductItem()
        item.name = d.get("name", "")
        item.price = d.get("price", "")
        item.original_price = d.get("original_price", "")
        item.review_count = d.get("review_count", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} products for '{request.query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name}")
        print(f"     Price: {item.price}  Was: {item.original_price}  Reviews: {item.review_count}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("containerstore")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_containerstore(page, ContainerStoreSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
