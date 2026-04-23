"""
Auto-generated Playwright script (Python)
Movoto – Real estate listing search

Uses CDP-launched Chrome to avoid bot detection.
Navigates to city listing page → extracts listings from innerText.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ListingSearchRequest:
    city: str = "denver"
    state: str = "co"
    max_results: int = 5


@dataclass
class Listing:
    address: str = ""
    price: str = ""
    bedrooms: str = ""
    bathrooms: str = ""
    sqft: str = ""


@dataclass
class ListingSearchResult:
    listings: List[Listing] = field(default_factory=list)


def listing_search(page: Page, request: ListingSearchRequest) -> ListingSearchResult:
    """Search Movoto for home listings."""
    print(f"  City:  {request.city}, {request.state.upper()}")
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Navigate to Movoto listings")
    page.goto(
        f"https://www.movoto.com/{request.city}-{request.state}/",
        wait_until="domcontentloaded",
    )
    page.wait_for_timeout(6000)

    checkpoint("Extract listing cards")
    listings_data = page.evaluate(
        r"""(max) => {
            const cards = document.querySelectorAll('[class*="card"]');
            const results = [];
            const seenAddresses = new Set();
            for (const card of cards) {
                if (results.length >= max) break;
                const text = card.innerText;
                // Each card: "ADDRESS\n$PRICE\nXBd\nYBa\nZ Sq Ft..."
                const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
                
                // Address: line containing "CO" (or state abbreviation) and a zip
                let address = '';
                for (const line of lines) {
                    if (/\b\d{5}\b/.test(line) && line.includes(',')) {
                        address = line;
                        break;
                    }
                }
                if (!address) continue;
                if (seenAddresses.has(address)) continue;
                seenAddresses.add(address);
                
                // Price: line starting with $
                let price = '';
                for (const line of lines) {
                    if (line.startsWith('$')) {
                        price = line;
                        break;
                    }
                }
                
                // Bedrooms: "XBd"
                const bdMatch = text.match(/(\d+)\s*Bd/);
                const bedrooms = bdMatch ? bdMatch[1] : '';
                
                // Bathrooms: "YBa"
                const baMatch = text.match(/(\d+)\s*Ba/);
                const bathrooms = baMatch ? baMatch[1] : '';
                
                // Sqft: "Z Sq Ft"
                const sqftMatch = text.match(/([\d,]+)\s*Sq\s*Ft/);
                const sqft = sqftMatch ? sqftMatch[1] : '';
                
                results.push({address, price, bedrooms, bathrooms, sqft});
            }
            return results;
        }""",
        request.max_results,
    )

    result = ListingSearchResult()
    for ld in listings_data:
        l = Listing()
        l.address = ld.get("address", "")
        l.price = ld.get("price", "")
        l.bedrooms = ld.get("bedrooms", "")
        l.bathrooms = ld.get("bathrooms", "")
        l.sqft = ld.get("sqft", "")
        result.listings.append(l)

    for i, l in enumerate(result.listings):
        print(f"  Listing {i + 1}:")
        print(f"    Address:  {l.address}")
        print(f"    Price:    {l.price}")
        print(f"    Beds:     {l.bedrooms}")
        print(f"    Baths:    {l.bathrooms}")
        print(f"    Sq Ft:    {l.sqft}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("movoto")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = ListingSearchRequest()
            result = listing_search(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.listings)} listings")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
