"""
Playwright script (Python) — Offers.com Coupons
Search Offers.com for Amazon coupon codes.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class OffersRequest:
    store: str = "amazon"
    max_results: int = 5


@dataclass
class OfferItem:
    description: str = ""
    discount: str = ""


@dataclass
class OffersResult:
    offers: List[OfferItem] = field(default_factory=list)


# Searches Offers.com for coupons and extracts offer description and discount.
def search_offers(page: Page, request: OffersRequest) -> OffersResult:
    url = f"https://www.offers.com/{request.store}/"
    print(f"Loading {url}...")
    checkpoint("Navigate to Offers.com")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = OffersResult()

    checkpoint("Extract coupon offers")
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find coupon groups: discount lines before "Details" / "SITEWIDE OFFER" / Title / "Get Offer"
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'Get Offer' && i >= 2) {
                // Title is 2 lines before "Get Offer"
                const title = lines[i - 1] || '';
                // Walk backwards to find discount percentage
                let discount = '';
                for (let j = i - 2; j >= Math.max(0, i - 8); j--) {
                    if (/^\\d+%$/.test(lines[j])) {
                        discount = lines[j] + ' off';
                        break;
                    }
                    if (lines[j] === 'SALE') {
                        discount = 'Sale';
                        break;
                    }
                }
                if (title.length > 10 && !/^(Why Trust|Learn How|Meet Our|Similar)/i.test(title)) {
                    results.push({ description: title, discount });
                }
            }
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = OfferItem()
        item.description = d.get("description", "")
        item.discount = d.get("discount", "")
        result.offers.append(item)

    print(f"\nFound {len(result.offers)} offers:")
    for i, o in enumerate(result.offers, 1):
        print(f"\n  {i}. {o.description}")
        print(f"     Discount: {o.discount}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("offers")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_offers(page, OffersRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.offers)} offers")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
