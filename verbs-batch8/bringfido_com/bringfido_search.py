"""
BringFido – Search for pet-friendly hotels by destination

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
class BringFidoSearchRequest:
    city: str = "san-francisco-ca"
    max_results: int = 5


@dataclass
class BringFidoHotelItem:
    hotel_name: str = ""
    address: str = ""
    rating: str = ""
    price_range: str = ""
    pet_policy: str = ""
    amenities: str = ""


@dataclass
class BringFidoSearchResult:
    items: List[BringFidoHotelItem] = field(default_factory=list)


# Search for pet-friendly hotels on BringFido by destination.
def bringfido_search(page: Page, request: BringFidoSearchRequest) -> BringFidoSearchResult:
    """Search for pet-friendly hotels on BringFido."""
    print(f"  City: {request.city}")
    print(f"  Max results: {request.max_results}\n")

    url = f"https://www.bringfido.com/lodging/?city=San+Francisco&state=CA"
    print(f"Loading {url}...")
    checkpoint("Navigate to BringFido lodging page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = BringFidoSearchResult()

    checkpoint("Extract pet-friendly hotel listings")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();
        const skip = new Set(['filters', 'hotels', 'airbnb', 'fetch', 'pet friendly hotels', 'pet friendly', 'top pet friendly hotels']);
        
        // Find hotel heading cards (h2/h3 that are hotel names)
        const headings = document.querySelectorAll('h2, h3');
        for (const h of headings) {
            if (items.length >= max) break;
            const title = h.innerText.trim();
            if (title.length < 5 || title.length > 100) continue;
            if (skip.has(title.toLowerCase()) || seen.has(title)) continue;
            seen.add(title);
            
            const card = h.closest('a, div, li, article') || h.parentElement;
            const fullText = card ? card.innerText.trim() : '';
            const lines = fullText.split('\\n').filter(l => l.trim());
            
            let address = '';
            let rating = '';
            let price = '';
            for (const line of lines) {
                if (line.match(/\\$/)) price = line;
                if (line.match(/\\d+\\.\\d|stars?/i)) rating = line;
                if (line.match(/,\\s*[A-Z]{2}/) && !address) address = line;
            }
            
            items.push({hotel_name: title, address, rating, price_range: price, pet_policy: '', amenities: ''});
        }
        
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = BringFidoHotelItem()
        item.hotel_name = d.get("hotel_name", "")
        item.address = d.get("address", "")
        item.rating = d.get("rating", "")
        item.price_range = d.get("price_range", "")
        item.pet_policy = d.get("pet_policy", "")
        item.amenities = d.get("amenities", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Hotel {i}:")
        print(f"    Name:       {item.hotel_name}")
        print(f"    Address:    {item.address}")
        print(f"    Rating:     {item.rating}")
        print(f"    Price:      {item.price_range}")
        print(f"    Pet Policy: {item.pet_policy}")
        print(f"    Amenities:  {item.amenities}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("bringfido")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = BringFidoSearchRequest()
            result = bringfido_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} hotels")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
