"""
Auto-generated Playwright script (Python)
Zillow – Rental Property Search
Location: "Austin, TX", Max Rent: $2000

Generated on: 2026-04-18T03:17:42.127Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import json
import os, sys, shutil
from dataclasses import dataclass, field
from urllib.parse import quote
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ZillowRequest:
    location: str = "Austin, TX"
    location_slug: str = "austin-tx"
    max_rent: int = 2000
    max_listings: int = 5


@dataclass
class RentalListing:
    address: str = ""
    monthly_rent: str = ""
    bedrooms: str = ""
    listing_url: str = ""


@dataclass
class ZillowResult:
    listings: list = field(default_factory=list)


def zillow_rentals(page: Page, request: ZillowRequest) -> ZillowResult:
    """Search Zillow for rental properties."""
    print(f"  Location: {request.location}")
    print(f"  Max Rent: ${request.max_rent}/mo\n")

    # ── Build search URL ──────────────────────────────────────────────
    filter_state = json.dumps({
        "pagination": {},
        "isMapVisible": True,
        "filterState": {
            "price": {"max": request.max_rent},
            "fr": {"value": True},
            "fsba": {"value": False},
            "fsbo": {"value": False},
            "nc": {"value": False},
            "cmsn": {"value": False},
            "auc": {"value": False},
            "fore": {"value": False},
        },
    })
    search_url = f"https://www.zillow.com/{request.location_slug}/rentals/?searchQueryState={quote(filter_state)}"
    print(f"Loading {search_url[:80]}...")
    checkpoint("Navigate to Zillow rentals")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)

    # ── Extract listings ──────────────────────────────────────────────
    raw = page.evaluate(r"""(maxListings) => {
        const cards = document.querySelectorAll('[data-test="property-card"]');
        const results = [];
        for (const card of cards) {
            if (results.length >= maxListings) break;
            const NL = String.fromCharCode(10);
            const lines = card.innerText.split(NL).filter(l => l.trim());
            if (lines.length < 3) continue;

            // First line: "$1,355+ 1 bd" or "$1,551+ Studio"
            const priceLine = lines[0];
            const priceMatch = priceLine.match(/(\$[\d,]+\+?)/);
            const rent = priceMatch ? priceMatch[1] : '';
            const bdMatch = priceLine.match(/(\d+\s*bd|Studio)/i);
            const bedrooms = bdMatch ? bdMatch[1] : '';

            // Address: line containing "TX" (after "Total monthly price")
            let address = '';
            for (const line of lines) {
                if (/,\s*TX/.test(line)) {
                    address = line.trim();
                    break;
                }
            }

            // URL from anchor
            const link = card.querySelector('a');
            const url = link ? link.href : '';

            if (rent && address) {
                results.push({ address, monthly_rent: rent, bedrooms, listing_url: url });
            }
        }
        return results;
    }""", request.max_listings)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Zillow Rentals: {request.location} (max ${request.max_rent}/mo)")
    print("=" * 60)
    for idx, r in enumerate(raw, 1):
        print(f"\n  {idx}. {r['address']}")
        print(f"     Rent:     {r['monthly_rent']}/mo")
        print(f"     Bedrooms: {r['bedrooms']}")
        print(f"     URL:      {r['listing_url']}")

    listings = [RentalListing(**r) for r in raw]
    return ZillowResult(listings=listings)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("zillow_com__rentals")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = zillow_rentals(page, ZillowRequest())
            print(f"\nReturned {len(result.listings)} listings")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
