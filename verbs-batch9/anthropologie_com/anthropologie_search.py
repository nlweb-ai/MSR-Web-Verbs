"""
Playwright script (Python) — Anthropologie Search
Search for products on Anthropologie.
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
class AnthropologieSearchRequest:
    query: str = "throw pillows"
    max_results: int = 5


@dataclass
class ProductItem:
    product_name: str = ""
    price: str = ""


@dataclass
class AnthropologieSearchResult:
    query: str = ""
    items: List[ProductItem] = field(default_factory=list)


def search_anthropologie(page: Page, request: AnthropologieSearchRequest) -> AnthropologieSearchResult:
    """Search Anthropologie for products."""
    encoded = quote_plus(request.query)
    url = f"https://www.anthropologie.com/search?q={encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = AnthropologieSearchResult(query=request.query)

    checkpoint("Extract products")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('.o-pwa-product-tile');
        for (const card of cards) {
            if (items.length >= max) break;
            const nameEl = card.querySelector('.o-pwa-product-tile__heading');
            const name = nameEl ? nameEl.textContent.trim() : '';
            if (!name) continue;

            const saleEl = card.querySelector('.c-pwa-product-price__current');
            const origEl = card.querySelector('.c-pwa-product-price__original');
            const price = saleEl ? saleEl.textContent.replace(/Sale price:/i, '').trim() : '';
            const origPrice = origEl ? origEl.textContent.replace(/Original price:/i, '').trim() : '';
            const fullPrice = origPrice ? price + ' (was ' + origPrice + ')' : price;

            items.push({product_name: name, price: fullPrice});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ProductItem()
        item.product_name = d.get("product_name", "")
        item.price = d.get("price", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} products for '{request.query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.product_name[:80]}")
        print(f"     Price: {item.price}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("anthropologie")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_anthropologie(page, AnthropologieSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
