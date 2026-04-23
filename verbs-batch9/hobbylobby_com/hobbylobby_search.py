"""
Playwright script (Python) — Hobby Lobby Product Search
Search Hobby Lobby for craft/art supplies.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class HobbyLobbyRequest:
    search_query: str = "acrylic paint"
    max_results: int = 5


@dataclass
class ProductItem:
    name: str = ""
    price: str = ""
    original_price: str = ""
    reviews: str = ""


@dataclass
class HobbyLobbyResult:
    query: str = ""
    items: List[ProductItem] = field(default_factory=list)


# Searches Hobby Lobby for products matching the query and returns
# up to max_results items with name, brand, price, and availability.
def search_hobbylobby(page: Page, request: HobbyLobbyRequest) -> HobbyLobbyResult:
    import urllib.parse
    url = f"https://www.hobbylobby.com/search/?text={urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = HobbyLobbyResult(query=request.search_query)

    checkpoint("Extract product listings")
    js_code = """(max) => {
        const results = [];
        const links = document.querySelectorAll('a[href*="/p/"]');
        const seen = new Set();
        for (const link of links) {
            if (results.length >= max) break;
            const lines = link.innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 4) continue;
            const name = lines[0].trim();
            if (!name || name.length < 3) continue;
            if (seen.has(name)) continue;
            seen.add(name);
            // lines: name, reviewCount, "reviews", priceLabel, priceValue, [origLabel, origValue]
            const reviews = (lines[1] && /^\\d+$/.test(lines[1].trim())) ? lines[1].trim() : '';
            // Find the price value line (first line starting with $)
            let price = '';
            let original_price = '';
            for (let i = 2; i < lines.length; i++) {
                const l = lines[i].trim();
                if (l.startsWith('$') || l.startsWith('Free')) {
                    if (!price) {
                        price = l;
                    } else if (!original_price) {
                        original_price = l;
                        break;
                    }
                }
            }
            // If we have "Current price range" + "Original price range", the first $ is current, second is original
            // But for "price:" items, there's only one $ line
            results.push({ name, price, original_price, reviews });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ProductItem()
        item.name = d.get("name", "")
        item.price = d.get("price", "")
        item.original_price = d.get("original_price", "")
        item.reviews = d.get("reviews", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} products for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name}")
        orig = f" (was {item.original_price})" if item.original_price else ""
        print(f"     Price: {item.price}{orig}  Reviews: {item.reviews}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("hobbylobby")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_hobbylobby(page, HobbyLobbyRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
