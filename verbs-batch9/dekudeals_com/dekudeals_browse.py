"""
Playwright script (Python) — Deku Deals Browse
Browse Nintendo Switch game deals on Deku Deals.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class DekuDealsBrowseRequest:
    max_results: int = 5


@dataclass
class GameDealItem:
    title: str = ""
    current_price: str = ""
    regular_price: str = ""
    discount: str = ""
    sale_ends: str = ""


@dataclass
class DekuDealsBrowseResult:
    items: List[GameDealItem] = field(default_factory=list)


def browse_dekudeals(page: Page, request: DekuDealsBrowseRequest) -> DekuDealsBrowseResult:
    """Browse Deku Deals for Nintendo Switch game deals."""
    url = "https://www.dekudeals.com/hottest"
    print(f"Loading {url}...")
    checkpoint("Navigate to deals")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = DekuDealsBrowseResult()

    checkpoint("Extract game deals")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();
        const links = document.querySelectorAll('a[href*="/items/"]');
        for (const link of links) {
            if (items.length >= max) break;
            const container = link.closest('.position-relative') || link.parentElement.parentElement.parentElement;
            if (!container) continue;
            const lines = container.innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 3) continue;
            const title = lines[0].trim();
            if (!title || title.length < 2 || seen.has(title)) continue;
            seen.add(title);
            const regularPrice = lines[1] || '';
            const salePrice = lines[2] || '';
            const discount = lines[3] || '';
            const saleEnds = '';
            for (const line of lines) {
                if (line.startsWith('Sale ends')) { break; }
            }
            let saleEndsVal = '';
            for (const line of lines) {
                if (line.startsWith('Sale ends')) { saleEndsVal = line; break; }
            }
            items.push({title, current_price: salePrice, regular_price: regularPrice, discount, sale_ends: saleEndsVal});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = GameDealItem()
        item.title = d.get("title", "")
        item.current_price = d.get("current_price", "")
        item.regular_price = d.get("regular_price", "")
        item.discount = d.get("discount", "")
        item.sale_ends = d.get("sale_ends", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} game deals:")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Price: {item.current_price} (was {item.regular_price}) {item.discount}")
        print(f"     {item.sale_ends}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("dekudeals")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = browse_dekudeals(page, DekuDealsBrowseRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} deals")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
