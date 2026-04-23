"""
Playwright script (Python) — GG.deals Game Deal Browser
Browse best current PC game deals on GG.deals.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GGDealsRequest:
    max_results: int = 5


@dataclass
class DealItem:
    title: str = ""
    original_price: str = ""
    current_price: str = ""
    discount: str = ""


@dataclass
class GGDealsResult:
    items: List[DealItem] = field(default_factory=list)


# Browses GG.deals for the best current PC game deals and returns
# up to max_results deals with title, store, current price, historical low, and discount.
def browse_ggdeals(page: Page, request: GGDealsRequest) -> GGDealsResult:
    url = "https://gg.deals/deals/"
    print(f"Loading {url}...")
    checkpoint("Navigate to deals page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = GGDealsResult()

    checkpoint("Extract deal listings")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        const cards = document.querySelectorAll('[data-deal-id]');
        for (const card of cards) {
            if (results.length >= max) break;
            const lines = card.innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 4) continue;
            const title = lines[0].trim();
            if (!title || title.length < 2 || seen.has(title)) continue;
            seen.add(title);
            let original_price = '', current_price = '', discount = '';
            for (const l of lines) {
                const t = l.trim();
                if (t.match(/^-\\d+%/)) { discount = t; continue; }
                if (t.match(/^\\$[\\d,.]+$/) && !original_price) { original_price = t; continue; }
                if ((t.match(/^[~]?\\$[\\d,.]+$/) || t === 'Free') && original_price && !current_price) { current_price = t; continue; }
            }
            results.push({title, original_price, current_price, discount});
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = DealItem()
        item.title = d.get("title", "")
        item.original_price = d.get("original_price", "")
        item.current_price = d.get("current_price", "")
        item.discount = d.get("discount", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} deals:")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Price: {item.current_price}  Was: {item.original_price}  Discount: {item.discount}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("ggdeals")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = browse_ggdeals(page, GGDealsRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} deals")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
