"""
Auto-generated Playwright script (Python)
Slickdeals – Search Deals
Query: "headphones"

Generated on: 2026-04-18T02:10:31.733Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class SlickdealsRequest:
    query: str = "headphones"
    max_deals: int = 5


@dataclass
class Deal:
    title: str = ""
    price: str = ""
    original_price: str = ""
    store: str = ""
    thumbs_up: str = ""


@dataclass
class SlickdealsResult:
    deals: list = field(default_factory=list)


def slickdeals_search(page: Page, request: SlickdealsRequest) -> SlickdealsResult:
    """Search slickdeals.net for deals."""
    print(f"  Query: {request.query}\n")

    # ── Search ────────────────────────────────────────────────────────
    search_url = f"https://slickdeals.net/newsearch.php?q={quote_plus(request.query)}&searcharea=deals&searchin=first"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to slickdeals search")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Extract deals ─────────────────────────────────────────────────
    raw_deals = page.evaluate(r"""(maxDeals) => {
        const cards = document.querySelectorAll('div.dealCardListView');
        const results = [];
        for (let i = 0; i < Math.min(cards.length, maxDeals); i++) {
            const card = cards[i];
            const titleEl = card.querySelector('a[class*="dealCardListView__title"]');
            const priceEl = card.querySelector('span.dealCardListView__finalPrice');
            const listPriceEl = card.querySelector('span.dealCardListView__listPrice');
            const storeEl = card.querySelector('div.dealCardListView__store');
            const voteEl = card.querySelector('span.dealCardListView__voteCount');

            results.push({
                title: titleEl ? titleEl.innerText.trim() : '',
                price: priceEl ? priceEl.innerText.trim() : '',
                original_price: listPriceEl ? listPriceEl.innerText.trim() : '',
                store: storeEl ? storeEl.innerText.trim() : '',
                thumbs_up: voteEl ? voteEl.innerText.trim() : '0',
            });
        }
        return results;
    }""", request.max_deals)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Slickdeals: {request.query}")
    print("=" * 60)
    for idx, d in enumerate(raw_deals, 1):
        print(f"\n  {idx}. {d['title']}")
        print(f"     Price: {d['price']}")
        if d['original_price']:
            print(f"     Was: {d['original_price']}")
        print(f"     Store: {d['store']}")
        print(f"     Thumbs up: {d['thumbs_up']}")

    deals = [Deal(**d) for d in raw_deals]
    return SlickdealsResult(deals=deals)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("slickdeals_net")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = slickdeals_search(page, SlickdealsRequest())
            print(f"\nReturned {len(result.deals)} deals")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
