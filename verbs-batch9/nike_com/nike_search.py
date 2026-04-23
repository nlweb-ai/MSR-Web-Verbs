"""
Playwright script (Python) — Nike Running Shoes Search
Search Nike for men's running shoes.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class NikeRequest:
    query: str = "running shoes men"
    max_results: int = 5


@dataclass
class ShoeItem:
    name: str = ""
    category: str = ""
    price: str = ""
    colors: str = ""


@dataclass
class NikeResult:
    products: List[ShoeItem] = field(default_factory=list)


# Searches Nike for running shoes and extracts shoe name,
# category, price, and color count.
def search_nike(page: Page, request: NikeRequest) -> NikeResult:
    url = "https://www.nike.com/w/mens-running-shoes-37v7jznik1zy7ok"
    print(f"Loading {url}...")
    checkpoint("Navigate to Nike running shoes")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)

    result = NikeResult()

    checkpoint("Extract product listings")
    js_code = """(max) => {
        const results = [];
        const cards = document.querySelectorAll('.product-card');
        for (const card of cards) {
            if (results.length >= max) break;
            const lines = card.innerText.split('\\n').map(l => l.trim()).filter(l => l);
            if (lines.length < 4) continue;
            const name = lines[0] || '';
            if (!name || name.length < 3) continue;
            let price = '', category = '', colors = '';
            for (let i = lines.length - 1; i >= 0; i--) {
                if (lines[i].startsWith('$') && !price) { price = lines[i]; }
                else if (lines[i].includes('Colors') && !colors) { colors = lines[i]; }
                else if (lines[i].includes('Shoes') && !category) { category = lines[i]; }
            }
            results.push({ name, category, price, colors });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ShoeItem()
        item.name = d.get("name", "")
        item.category = d.get("category", "")
        item.price = d.get("price", "")
        item.colors = d.get("colors", "")
        result.products.append(item)

    print(f"\nFound {len(result.products)} products:")
    for i, p in enumerate(result.products, 1):
        print(f"\n  {i}. {p.name}")
        print(f"     Category: {p.category}  Price: {p.price}  Colors: {p.colors}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("nike")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_nike(page, NikeRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.products)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
