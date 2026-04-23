"""
Playwright script (Python) — eBay Motors Search
Search eBay Motors for vehicle listings.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class EbayMotorsSearchRequest:
    search_query: str = "Toyota Camry"
    max_price: int = 20000
    max_results: int = 5


@dataclass
class VehicleListingItem:
    title: str = ""
    price: str = ""
    mileage: str = ""
    year: str = ""
    location: str = ""
    listing_type: str = ""


@dataclass
class EbayMotorsSearchResult:
    query: str = ""
    items: List[VehicleListingItem] = field(default_factory=list)


def search_ebay_motors(page: Page, request: EbayMotorsSearchRequest) -> EbayMotorsSearchResult:
    """Search eBay Motors for vehicles."""
    url = f"https://www.ebay.com/sch/Cars-Trucks/6001/i.html?_nkw={request.search_query.replace(' ', '+')}&_udhi={request.max_price}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = EbayMotorsSearchResult(query=request.search_query)

    checkpoint("Extract vehicle listings")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();
        const cards = document.querySelectorAll('li.s-card');
        for (const card of cards) {
            if (items.length >= max) break;
            const lines = card.innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 3) continue;
            const title = lines[0].trim();
            if (!title || title === 'Shop on eBay' || title.length < 5) continue;
            if (seen.has(title)) continue;
            seen.add(title);
            let price = '', year = '', mileage = '', location = '', listingType = '';
            const yrMatch = title.match(/((?:19|20)\\d{2})/);
            if (yrMatch) year = yrMatch[1];
            for (const line of lines) {
                const l = line.trim();
                if (l.startsWith('$') && !price) price = l;
                if (l.startsWith('Miles:')) mileage = l.replace('Miles: ', '').trim();
                if (l.startsWith('Located in')) location = l.replace('Located in ', '').trim();
                if (l === 'Buy It Now') listingType = 'Buy It Now';
                if (l.match(/^\\d+ bids/)) listingType = l;
            }
            items.push({title, price, mileage, year, location, listing_type: listingType});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = VehicleListingItem()
        item.title = d.get("title", "")
        item.price = d.get("price", "")
        item.mileage = d.get("mileage", "")
        item.year = d.get("year", "")
        item.location = d.get("location", "")
        item.listing_type = d.get("listing_type", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} vehicles for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Price: {item.price}  Year: {item.year}  Mileage: {item.mileage}")
        print(f"     Location: {item.location}  Type: {item.listing_type}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("ebay_motors")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_ebay_motors(page, EbayMotorsSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} vehicles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
