"""
Etsy – Search for vintage items

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class EtsyVintageSearchRequest:
    search_query: str = "vintage jewelry"
    max_results: int = 5


@dataclass
class EtsyVintageItem:
    item_name: str = ""
    shop_name: str = ""
    price: str = ""
    original_price: str = ""
    rating: str = ""
    num_reviews: str = ""
    is_free_shipping: str = ""


@dataclass
class EtsyVintageSearchResult:
    items: List[EtsyVintageItem] = field(default_factory=list)


# Search for vintage items on Etsy.
def etsy_vintage_search(page: Page, request: EtsyVintageSearchRequest) -> EtsyVintageSearchResult:
    """Search for vintage items on Etsy."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://www.etsy.com/search?q={query}&explicit=1&is_vintage=true"
    print(f"Loading {url}...")
    checkpoint("Navigate to Etsy vintage search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = EtsyVintageSearchResult()

    checkpoint("Extract vintage item listings")
    js_code = r"""(max) => {
        const items = [];
        const seen = new Set();
        
        // Find listing links
        const links = document.querySelectorAll('a[href*="/listing/"]');
        for (const a of links) {
            if (items.length >= max) break;
            const title = a.getAttribute('title') || a.innerText.trim().split('\n')[0].trim();
            if (title.length < 5 || seen.has(title)) continue;
            seen.add(title);
            
            const card = a.closest('li, div[class]') || a;
            const fullText = card.innerText.trim();
            
            let price = '';
            let shop = '';
            const priceMatch = fullText.match(/\$[\d,.]+/);
            if (priceMatch) price = priceMatch[0];
            
            items.push({item_name: title, shop_name: shop, price, original_price: '', rating: '', num_reviews: '', is_free_shipping: 'No'});
        }
        
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = EtsyVintageItem()
        item.item_name = d.get("item_name", "")
        item.shop_name = d.get("shop_name", "")
        item.price = d.get("price", "")
        item.original_price = d.get("original_price", "")
        item.rating = d.get("rating", "")
        item.num_reviews = d.get("num_reviews", "")
        item.is_free_shipping = d.get("is_free_shipping", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Item {i}:")
        print(f"    Name:          {item.item_name}")
        print(f"    Shop:          {item.shop_name}")
        print(f"    Price:         {item.price}")
        print(f"    Original:      {item.original_price}")
        print(f"    Rating:        {item.rating}")
        print(f"    Reviews:       {item.num_reviews}")
        print(f"    Free Shipping: {item.is_free_shipping}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("etsy_vintage")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = EtsyVintageSearchRequest()
            result = etsy_vintage_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} vintage items")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
