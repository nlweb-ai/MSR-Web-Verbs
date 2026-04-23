"""
Playwright script (Python) — Fashionphile Pre-Owned Luxury Search
Search for pre-owned luxury items on Fashionphile.com.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class FashionphileSearchRequest:
    search_query: str = "Louis Vuitton"
    max_results: int = 5


@dataclass
class LuxuryItem:
    name: str = ""
    condition: str = ""
    price: str = ""
    retail_price: str = ""
    savings: str = ""


@dataclass
class FashionphileSearchResult:
    query: str = ""
    items: List[LuxuryItem] = field(default_factory=list)


# Searches Fashionphile.com for pre-owned luxury items matching the query and returns
# up to max_results listings with name, condition, price, retail price, and savings.
def search_fashionphile(page: Page, request: FashionphileSearchRequest) -> FashionphileSearchResult:
    import urllib.parse
    url = f"https://www.fashionphile.com/shop?search={urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = FashionphileSearchResult(query=request.search_query)

    checkpoint("Extract luxury item listings")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        const cards = document.querySelectorAll('div.fp-algolia-product-card');
        for (const card of cards) {
            if (results.length >= max) break;
            const lines = card.innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 3) continue;
            const brand = lines[0].trim();
            const productName = lines[1] ? lines[1].trim() : '';
            const name = brand + ' ' + productName;
            if (!name || name.length < 5) continue;
            if (seen.has(name)) continue;
            seen.add(name);
            const condition = lines[2] ? lines[2].trim() : '';
            const price = lines[3] ? lines[3].trim() : '';
            const retail_price = (lines[4] && lines[4].includes('Retail')) ? lines[4].replace('Est. Retail ', '').trim() : '';
            const savings = (lines[5] && lines[5].includes('below')) ? lines[5].trim() : '';
            results.push({name, condition, price, retail_price, savings});
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = LuxuryItem()
        item.name = d.get("name", "")
        item.condition = d.get("condition", "")
        item.price = d.get("price", "")
        item.retail_price = d.get("retail_price", "")
        item.savings = d.get("savings", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} items for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name}")
        print(f"     Condition: {item.condition}  Price: {item.price}")
        print(f"     Retail: {item.retail_price}  Savings: {item.savings}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("fashionphile")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_fashionphile(page, FashionphileSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} items")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
