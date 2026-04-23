"""
Playwright script (Python) — Amazon Subscribe & Save
Browse Subscribe & Save deals by category.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class AmazonSubscribeSaveRequest:
    category: str = "baby"
    max_results: int = 5


@dataclass
class SubscribeSaveItem:
    product_name: str = ""
    regular_price: str = ""
    subscribe_price: str = ""
    discount_pct: str = ""


@dataclass
class AmazonSubscribeSaveResult:
    category: str = ""
    items: List[SubscribeSaveItem] = field(default_factory=list)


# Browses Amazon Subscribe & Save deals in a category.
def browse_subscribe_save(page: Page, request: AmazonSubscribeSaveRequest) -> AmazonSubscribeSaveResult:
    """Browse Amazon Subscribe & Save."""
    encoded = quote_plus(request.category)
    url = f"https://www.amazon.com/s?k={encoded}+subscribe+and+save"
    print(f"Loading {url}...")
    checkpoint("Navigate to Subscribe & Save")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = AmazonSubscribeSaveResult(category=request.category)

    checkpoint("Extract S&S items")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('[data-component-type="s-search-result"]');
        for (const card of cards) {
            if (items.length >= max) break;
            const text = (card.textContent || '').replace(/\\s+/g, ' ').trim();

            let name = '';
            const nameEl = card.querySelector('h2 a span, h2 span');
            if (nameEl) name = nameEl.textContent.trim();

            let regPrice = '';
            const regEl = card.querySelector('.a-price[data-a-strike="true"] .a-offscreen, .a-text-price .a-offscreen');
            if (regEl) regPrice = regEl.textContent.trim();

            let subPrice = '';
            const priceEl = card.querySelector('.a-price:not([data-a-strike]) .a-offscreen');
            if (priceEl) subPrice = priceEl.textContent.trim();

            let discount = '';
            const discMatch = text.match(/(\\d+)%\\s*off/i);
            if (discMatch) discount = discMatch[1] + '%';
            if (!discount) {
                const snsMatch = text.match(/Save\\s*(\\d+)%/i);
                if (snsMatch) discount = snsMatch[1] + '%';
            }

            if (name) items.push({product_name: name, regular_price: regPrice, subscribe_price: subPrice, discount_pct: discount});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = SubscribeSaveItem()
        item.product_name = d.get("product_name", "")
        item.regular_price = d.get("regular_price", "")
        item.subscribe_price = d.get("subscribe_price", "")
        item.discount_pct = d.get("discount_pct", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} Subscribe & Save items in '{request.category}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.product_name[:80]}")
        print(f"     Regular: {item.regular_price}  S&S: {item.subscribe_price}  Discount: {item.discount_pct}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("amazon_sns")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = browse_subscribe_save(page, AmazonSubscribeSaveRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} items")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
