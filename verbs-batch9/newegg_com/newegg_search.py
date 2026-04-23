"""
Playwright script (Python) — Newegg Product Search
Search Newegg for products like graphics cards.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class NeweggRequest:
    query: str = "graphics cards"
    max_results: int = 5


@dataclass
class ProductItem:
    name: str = ""
    price: str = ""


@dataclass
class NeweggResult:
    products: List[ProductItem] = field(default_factory=list)


# Searches Newegg for products and extracts name, brand,
# price, rating, reviews, and specs.
def search_newegg(page: Page, request: NeweggRequest) -> NeweggResult:
    url = f"https://www.newegg.com/p/pl?d={request.query.replace(' ', '+')}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Newegg search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = NeweggResult()

    checkpoint("Extract product listings")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        const items = document.querySelectorAll('.item-cell');
        for (const item of items) {
            if (results.length >= max) break;
            const titleEl = item.querySelector('.item-title, a[class*="title"]');
            const name = titleEl ? titleEl.textContent.trim() : '';
            if (!name || name.length < 10 || seen.has(name)) continue;
            seen.add(name);
            const lines = item.innerText.split('\\n').map(l => l.trim()).filter(l => l);
            // Find price: second line starting with $ (first is original, second is sale)
            const priceLines = lines.filter(l => /^\\$[\\d,]+\\.\\d{2}/.test(l));
            const price = priceLines.length > 1 ? priceLines[1].trim() : (priceLines[0] || '');
            results.push({ name, price });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ProductItem()
        item.name = d.get("name", "")
        item.price = d.get("price", "")
        result.products.append(item)

    print(f"\nFound {len(result.products)} products:")
    for i, p in enumerate(result.products, 1):
        print(f"\n  {i}. {p.name}")
        print(f"     Price: {p.price}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("newegg")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_newegg(page, NeweggRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.products)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
