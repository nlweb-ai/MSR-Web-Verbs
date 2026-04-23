"""
Auto-generated Playwright script (Python)
Compass – Home Listings Search
Location: "brooklyn-ny"

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
class ListingSearchRequest:
    location: str = "brooklyn-ny"
    max_listings: int = 5


@dataclass
class Listing:
    address: str = ""
    neighborhood: str = ""
    price: str = ""
    bedrooms: str = ""
    bathrooms: str = ""
    sqft: str = ""


@dataclass
class ListingSearchResult:
    listings: List[Listing] = field(default_factory=list)


def compass_search(page: Page, request: ListingSearchRequest) -> ListingSearchResult:
    """Search Compass for home listings."""
    print(f"  Location: {request.location}\n")

    # ── Navigate to listings ──────────────────────────────────────────
    url = f"https://www.compass.com/homes-for-sale/{request.location}/"
    print(f"Loading {url}...")
    checkpoint("Navigate to Compass listings")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = ListingSearchResult()

    # ── Extract listings from cards ───────────────────────────────────
    checkpoint("Extract listing cards")
    js_code = r"""(max) => {
        const cards = document.querySelectorAll('[data-testid="cx-react-listingCard"]');
        const items = [];
        for (let i = 0; i < Math.min(cards.length, max); i++) {
            const card = cards[i];
            const text = card.innerText;
            const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);

            const priceMatch = text.match(/\$[\d,]+/);
            const price = priceMatch ? priceMatch[0] : '';

            const bedMatch = text.match(/(\d+)\s*\n?\s*Bedroom/i) || text.match(/(\d+)\s*\n?\s*bed/i);
            const bathMatch = text.match(/(\d+)\s*\n?\s*Bathroom/i) || text.match(/(\d+)\s*\n?\s*bath/i);
            const beds = bedMatch ? bedMatch[1] : '';
            const baths = bathMatch ? bathMatch[1] : '';

            const sqftMatch = text.match(/([\d,]+)\s*\n?\s*Square\s*Feet/i);
            const sqft = sqftMatch ? sqftMatch[1] : 'Unavailable';

            let address = '';
            for (const line of lines) {
                if (line.match(/\d+\s+\w+\s+(Street|St|Avenue|Ave|Place|Pl|Court|Ct|Drive|Dr|Road|Rd|Way|Blvd|Boulevard|Lane|Ln)/i) ||
                    line.match(/^\d+\s+[A-Z]/)) {
                    address = line;
                    break;
                }
            }
            let neighborhood = '';
            const addrIdx = lines.indexOf(address);
            if (addrIdx >= 0 && addrIdx + 1 < lines.length) {
                const next = lines[addrIdx + 1];
                if (!next.match(/^\$/) && !next.match(/^\d+$/) && next.length < 50) {
                    neighborhood = next;
                }
            }

            items.push({price, beds, baths, sqft, address, neighborhood});
        }
        return items;
    }"""
    listings_data = page.evaluate(js_code, request.max_listings)

    for ld in listings_data:
        listing = Listing()
        listing.address = ld.get("address", "")
        listing.neighborhood = ld.get("neighborhood", "")
        listing.price = ld.get("price", "")
        listing.bedrooms = ld.get("beds", "")
        listing.bathrooms = ld.get("baths", "")
        listing.sqft = ld.get("sqft", "Unavailable")
        result.listings.append(listing)

    # ── Print results ─────────────────────────────────────────────────
    for i, l in enumerate(result.listings, 1):
        print(f"\n  Listing {i}:")
        print(f"    Address:      {l.address}")
        print(f"    Neighborhood: {l.neighborhood}")
        print(f"    Price:        {l.price}")
        print(f"    Bedrooms:     {l.bedrooms}")
        print(f"    Bathrooms:    {l.bathrooms}")
        print(f"    Sqft:         {l.sqft}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("compass")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = ListingSearchRequest()
            result = compass_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.listings)} listings")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
