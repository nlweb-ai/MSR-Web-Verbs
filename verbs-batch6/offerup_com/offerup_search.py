"""
Auto-generated Playwright script (Python)
OfferUp – Listing Search
Query: "used bicycle"
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ListingRequest:
    query: str = "used bicycle"
    max_results: int = 5


@dataclass
class Listing:
    title: str = ""
    price: str = ""
    location: str = ""
    url: str = ""


@dataclass
class ListingResult:
    listings: List[Listing] = field(default_factory=list)


def offerup_search(page: Page, request: ListingRequest) -> ListingResult:
    """Search OfferUp for listings via Google site search."""
    print(f"  Query: {request.query}\n")

    from urllib.parse import quote_plus
    url = f"https://www.google.com/search?q=site%3Aofferup.com+{quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Google site search for OfferUp")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    checkpoint("Extract listing results from Google")
    listings_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();
        const h3s = document.querySelectorAll('h3');
        for (const h of h3s) {
            if (results.length >= maxResults) break;
            let text = h.innerText.trim();
            text = text.replace(/\s*[\|\u2013\u2014-]\s*OfferUp.*$/i, '').trim();
            if (text.length < 3 || seen.has(text)) continue;
            seen.add(text);

            let url = '';
            const link = h.closest('a') || h.parentElement?.closest('a');
            if (link) url = link.href || '';

            // Try to extract price from title
            let price = '';
            const pm = text.match(/(\$[\d,]+)/);
            if (pm) price = pm[1];

            results.push({ title: text.slice(0, 120), price, location: '', url });
        }
        return results;
    }""", request.max_results)

    listings = [Listing(**d) for d in listings_data]
    result = ListingResult(listings=listings[:request.max_results])

    print("\n" + "=" * 60)
    print(f"OfferUp: {request.query}")
    print("=" * 60)
    for i, l in enumerate(result.listings, 1):
        print(f"  {i}. {l.title}")
        if l.price:
            print(f"     Price:    {l.price}")
        if l.location:
            print(f"     Location: {l.location}")
        if l.url:
            print(f"     URL:      {l.url}")
    print(f"\nTotal: {len(result.listings)} listings")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("offerup_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = offerup_search(page, ListingRequest())
            print(f"\nReturned {len(result.listings)} listings")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
