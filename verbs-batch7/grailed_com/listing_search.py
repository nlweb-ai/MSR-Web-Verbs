"""
Auto-generated Playwright script (Python)
Grailed – Search fashion listings

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, urllib.parse
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ListingSearchRequest:
    search_query: str = "Rick Owens"
    max_results: int = 5


@dataclass
class Listing:
    name: str = ""
    designer: str = ""
    size: str = ""
    price: str = ""
    url: str = ""


@dataclass
class ListingSearchResult:
    listings: List[Listing] = field(default_factory=list)


def listing_search(page: Page, request: ListingSearchRequest) -> ListingSearchResult:
    """Search Grailed for fashion items and extract listings."""
    print(f"  Query: {request.search_query}")
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Navigate to Grailed search")
    q = urllib.parse.quote_plus(request.search_query)
    page.goto(f"https://www.grailed.com/shop?query={q}", wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    checkpoint("Extract listings")
    result = ListingSearchResult()

    items = page.evaluate(
        r"""(max) => {
            const cards = document.querySelectorAll('[class*="UserItem_root"]');
            const results = [];
            for (let i = 0; i < cards.length && results.length < max; i++) {
                const card = cards[i];

                // Designer
                const designerEl = card.querySelector('[class*="UserItem_designer"]');
                const designer = designerEl ? designerEl.textContent.trim() : '';

                // Size
                const sizeEl = card.querySelector('[class*="UserItem_size"]');
                const size = sizeEl ? sizeEl.textContent.trim() : '';

                // Title/name
                const titleEl = card.querySelector('[class*="UserItem_title"]');
                const name = titleEl ? titleEl.textContent.trim() : '';

                // Price
                const priceEl = card.querySelector('[data-testid="Current"]');
                const price = priceEl ? priceEl.textContent.trim() : '';

                // URL
                const linkEl = card.querySelector('a[href*="/listings/"]');
                let url = linkEl ? linkEl.href : '';
                // Strip tracking params
                if (url.includes('?')) url = url.split('?')[0];

                if (name || designer) {
                    results.push({name, designer, size, price, url});
                }
            }
            return results;
        }""",
        request.max_results,
    )

    for item in items:
        l = Listing()
        l.name = item.get("name", "")
        l.designer = item.get("designer", "")
        l.size = item.get("size", "")
        l.price = item.get("price", "")
        l.url = item.get("url", "")
        result.listings.append(l)

    for i, l in enumerate(result.listings):
        print(f"  Listing {i + 1}:")
        print(f"    Name:     {l.name}")
        print(f"    Designer: {l.designer}")
        print(f"    Size:     {l.size}")
        print(f"    Price:    {l.price}")
        print(f"    URL:      {l.url}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("grailed")
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
