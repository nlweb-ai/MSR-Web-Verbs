"""
Playwright script (Python) — Nordstrom Dress Shoes Search
Search Nordstrom for men's dress shoes.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class NordstromRequest:
    query: str = "men's dress shoes"
    max_results: int = 5


@dataclass
class ProductItem:
    name: str = ""
    price: str = ""
    rating: str = ""
    num_reviews: str = ""


@dataclass
class NordstromResult:
    products: List[ProductItem] = field(default_factory=list)


# Searches Nordstrom for dress shoes and extracts product name,
# price, rating, and number of reviews.
def search_nordstrom(page: Page, request: NordstromRequest) -> NordstromResult:
    url = f"https://www.nordstrom.com/sr?origin=keywordsearch&keyword={request.query.replace(' ', '+')}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Nordstrom search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)

    result = NordstromResult()

    checkpoint("Extract product listings")
    js_code = """(max) => {
        const results = [];
        const articles = document.querySelectorAll('article');
        for (const el of articles) {
            if (results.length >= max) break;
            const lines = el.innerText.split('\\n').map(l => l.trim()).filter(l => l);
            if (lines.length < 2) continue;
            let name = '', price = '', rating = '', num_reviews = '';
            for (const line of lines) {
                if (!name && line.length > 10 && !line.startsWith('$') && !line.startsWith('Current') && !line.startsWith('Previous') && !line.startsWith('Sponsored') && !line.startsWith('Nordstrom For') && !line.startsWith('Add to') && !/^\\d+\\.\\d+$/.test(line) && !/^\\(\\d+\\)$/.test(line)) {
                    name = line;
                } else if (!price && line.startsWith('$')) {
                    price = line;
                } else if (!rating && /^\\d+\\.\\d+$/.test(line)) {
                    rating = line;
                } else if (!num_reviews && /^\\(\\d+\\)$/.test(line)) {
                    num_reviews = line.replace(/[()]/g, '');
                }
            }
            if (!name) continue;
            results.push({ name, price, rating, num_reviews });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ProductItem()
        item.name = d.get("name", "")
        item.price = d.get("price", "")
        item.rating = d.get("rating", "")
        item.num_reviews = d.get("num_reviews", "")
        result.products.append(item)

    print(f"\nFound {len(result.products)} products:")
    for i, p in enumerate(result.products, 1):
        print(f"\n  {i}. {p.name}")
        print(f"     Price: {p.price}  Rating: {p.rating} ({p.num_reviews})")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("nordstrom")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_nordstrom(page, NordstromRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.products)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
