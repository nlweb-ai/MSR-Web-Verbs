"""
Auto-generated Playwright script (Python)
Depop – Item Search
Query: "vintage denim jacket"

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
class ItemSearchRequest:
    query: str = "vintage denim jacket"
    max_results: int = 5


@dataclass
class Listing:
    item_name: str = ""
    brand: str = ""
    price: str = ""
    size: str = ""
    seller: str = ""


@dataclass
class ItemSearchResult:
    listings: List[Listing] = field(default_factory=list)


def depop_search(page: Page, request: ItemSearchRequest) -> ItemSearchResult:
    """Search Depop for items."""
    print(f"  Query: {request.query}")
    print(f"  Max results: {request.max_results}\n")

    # ── Navigate to search page ───────────────────────────────────────
    query_encoded = request.query.replace(" ", "+")
    url = f"https://www.depop.com/search/?q={query_encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Depop search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = ItemSearchResult()

    # ── Extract listings from product cards ───────────────────────────
    checkpoint("Extract product cards")
    js_code = r"""(max) => {
        const cards = document.querySelectorAll('[class*="productCardRoot"]');
        const items = [];
        for (let i = 0; i < cards.length && items.length < max; i++) {
            const card = cards[i];
            const text = card.innerText.trim();
            const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);

            // Get product link for slug parsing
            const link = card.querySelector('a[href*="/products/"]');
            const href = link ? link.getAttribute('href') : '';
            const slug = href.replace('/products/', '').replace(/\/$/, '');

            // Parse seller (first segment) and item name from slug
            const parts = slug.split('-');
            const seller = parts.length > 0 ? parts[0] : '';
            // Remove seller (first) and hash ID (last) from slug for item name
            const itemParts = parts.length > 2 ? parts.slice(1, -1) : parts.slice(1);
            const itemName = itemParts.join(' ').replace(/\b\w/g, c => c.toUpperCase());

            // Card text: Brand, Size, Price (and optionally sale price)
            const brand = lines.length > 0 ? lines[0] : '';
            const size = lines.length > 1 ? lines[1] : '';
            const priceLine = lines.find(l => l.startsWith('$'));
            const price = priceLine || '';

            items.push({item_name: itemName, brand, price, size, seller});
        }
        return items;
    }"""
    listings_data = page.evaluate(js_code, request.max_results)

    for ld in listings_data:
        listing = Listing()
        listing.item_name = ld.get("item_name", "")
        listing.brand = ld.get("brand", "")
        listing.price = ld.get("price", "")
        listing.size = ld.get("size", "")
        listing.seller = ld.get("seller", "")
        result.listings.append(listing)

    # ── Print results ─────────────────────────────────────────────────
    for i, l in enumerate(result.listings, 1):
        print(f"\n  Listing {i}:")
        print(f"    Item:   {l.item_name}")
        print(f"    Brand:  {l.brand}")
        print(f"    Price:  {l.price}")
        print(f"    Size:   {l.size}")
        print(f"    Seller: {l.seller}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("depop")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = ItemSearchRequest()
            result = depop_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.listings)} listings")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
