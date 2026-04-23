"""
Playwright script (Python) — Homes.com Property Search
Search Homes.com for homes for sale.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class HomesSearchRequest:
    location: str = "Portland, OR"
    max_results: int = 5


@dataclass
class ListingItem:
    address: str = ""
    price: str = ""
    beds: str = ""
    baths: str = ""
    sqft: str = ""


@dataclass
class HomesSearchResult:
    location: str = ""
    items: List[ListingItem] = field(default_factory=list)


# Searches Homes.com for homes for sale in the given location and returns
# up to max_results listings with address, price, beds, baths, sqft, and year built.
def search_homes(page: Page, request: HomesSearchRequest) -> HomesSearchResult:
    location_slug = request.location.lower().replace(", ", "-").replace(" ", "-")
    url = f"https://www.homes.com/{location_slug}/"
    print(f"Loading {url}...")
    checkpoint("Navigate to listings")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = HomesSearchResult(location=request.location)

    checkpoint("Extract property listings")
    js_code = """(max) => {
        const results = [];
        const placards = document.querySelectorAll('[class*="placard"]');
        const seen = new Set();
        for (const card of placards) {
            if (results.length >= max) break;
            const lines = card.innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 5 || lines.length > 20) continue;
            let price = '', beds = '', baths = '', sqft = '', address = '';
            for (let i = 0; i < lines.length; i++) {
                const l = lines[i].trim();
                if (/^\\$[\\d,]+/.test(l) && !price) price = l;
                else if (/^\\d+(\\.\\d+)?\\s+Beds?$/i.test(l)) beds = l.split(/\\s/)[0];
                else if (/^\\d+(\\.\\d+)?\\s+Baths?$/i.test(l)) baths = l.split(/\\s/)[0];
                else if (/Sq\\s*Ft$/i.test(l)) sqft = l.replace(/\\s*Sq\\s*Ft$/i, '');
                else if (/^\\d+\\s+\\w.*,\\s*[A-Z]{2}\\s+\\d{5}/.test(l) && !address) address = l;
            }
            if (!address || !price) continue;
            if (seen.has(address)) continue;
            seen.add(address);
            results.push({ address, price, beds, baths, sqft });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ListingItem()
        item.address = d.get("address", "")
        item.price = d.get("price", "")
        item.beds = d.get("beds", "")
        item.baths = d.get("baths", "")
        item.sqft = d.get("sqft", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} listings in '{request.location}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.address}")
        print(f"     Price: {item.price}  Beds: {item.beds}  Baths: {item.baths}")
        print(f"     Sqft: {item.sqft}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("homes")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_homes(page, HomesSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} listings")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
