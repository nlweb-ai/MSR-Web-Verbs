"""
Auto-generated Playwright script (Python)
eBay – Completed/Sold Listings Search
Query: "Nintendo Switch OLED"

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
class SoldSearchRequest:
    query: str = "Nintendo Switch OLED"
    max_results: int = 5


@dataclass
class SoldItem:
    title: str = ""
    sold_price: str = ""
    sold_date: str = ""
    condition: str = ""


@dataclass
class SoldSearchResult:
    items: List[SoldItem] = field(default_factory=list)


def ebay_sold_search(page: Page, request: SoldSearchRequest) -> SoldSearchResult:
    """Search eBay for completed/sold listings."""
    print(f"  Query: {request.query}")
    print(f"  Max results: {request.max_results}\n")

    # ── Navigate to sold listings ─────────────────────────────────────
    query_encoded = request.query.replace(" ", "+")
    url = f"https://www.ebay.com/sch/i.html?_nkw={query_encoded}&LH_Complete=1&LH_Sold=1"
    print(f"Loading {url}...")
    checkpoint("Navigate to eBay sold listings")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = SoldSearchResult()

    # ── Extract sold items from cards ─────────────────────────────────
    checkpoint("Extract sold listing cards")
    js_code = r"""(max) => {
        const cards = document.querySelectorAll('li.s-card[data-listingid]');
        const items = [];
        for (const card of cards) {
            if (items.length >= max) break;
            const text = card.innerText.trim();
            const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);

            // Skip sponsored/ad cards (don't start with "Sold")
            if (!lines[0] || !lines[0].startsWith('Sold')) continue;

            const soldDate = lines[0].replace('Sold ', '');
            const title = lines[1] || '';

            // Condition is in a line with " · " separator
            let condition = '';
            const condLine = lines.find(l => l.includes(' · '));
            if (condLine) {
                condition = condLine.split(' · ')[0].trim();
            }

            // Price is the first line starting with "$"
            const priceLine = lines.find(l => /^\$[\d,]+/.test(l));
            const soldPrice = priceLine || '';

            items.push({title, sold_price: soldPrice, sold_date: soldDate, condition});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for id_ in items_data:
        item = SoldItem()
        item.title = id_.get("title", "")
        item.sold_price = id_.get("sold_price", "")
        item.sold_date = id_.get("sold_date", "")
        item.condition = id_.get("condition", "")
        result.items.append(item)

    # ── Print results ─────────────────────────────────────────────────
    for i, item in enumerate(result.items, 1):
        print(f"\n  Item {i}:")
        print(f"    Title:     {item.title}")
        print(f"    Price:     {item.sold_price}")
        print(f"    Sold Date: {item.sold_date}")
        print(f"    Condition: {item.condition}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("ebay_sold")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SoldSearchRequest()
            result = ebay_sold_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} sold items")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
