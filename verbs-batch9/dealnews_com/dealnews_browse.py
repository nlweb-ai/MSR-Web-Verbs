"""
Playwright script (Python) — DealNews Browse
Browse deals by category on DealNews.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class DealNewsBrowseRequest:
    category: str = "electronics"
    max_results: int = 5


@dataclass
class DealItem:
    product_name: str = ""
    store: str = ""
    sale_price: str = ""
    original_price: str = ""
    popularity: str = ""


@dataclass
class DealNewsBrowseResult:
    category: str = ""
    items: List[DealItem] = field(default_factory=list)


def browse_dealnews(page: Page, request: DealNewsBrowseRequest) -> DealNewsBrowseResult:
    """Browse DealNews for deals by category."""
    cat_map = {"electronics": "c142/Electronics"}
    slug = cat_map.get(request.category.lower(), f"c/{request.category}")
    url = f"https://www.dealnews.com/{slug}/"
    print(f"Loading {url}...")
    checkpoint("Navigate to deals")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = DealNewsBrowseResult(category=request.category)

    # Scroll all cards into view to defeat content-visibility:auto
    page.evaluate("""() => {
        const cards = document.querySelectorAll('.content-card');
        for (const c of cards) c.scrollIntoView();
        window.scrollTo(0, 0);
    }""")
    page.wait_for_timeout(1000)

    checkpoint("Extract deals")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();
        const cards = document.querySelectorAll('.content-card');
        for (const card of cards) {
            if (items.length >= max) break;
            const lines = card.innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 3) continue;

            // Find store line: contains " · " with "ago"
            let store = '', title = '', storeIdx = -1;
            for (let i = 0; i < Math.min(3, lines.length); i++) {
                if (lines[i].includes(' \\u00b7 ') && lines[i].match(/ago$/i)) {
                    store = lines[i].split(' \\u00b7 ')[0].trim();
                    storeIdx = i;
                    break;
                }
            }
            // Title is the line after the store line
            if (storeIdx >= 0 && storeIdx + 1 < lines.length) {
                title = lines[storeIdx + 1].trim();
            }
            if (!title || title.length < 5 || title.length > 300) continue;
            if (seen.has(title)) continue;
            seen.add(title);

            // Find prices: look for $XX patterns in all lines
            let salePrice = '', origPrice = '';
            const allText = lines.join(' ');
            const priceMatches = allText.match(/\\$[\\d,.]+/g) || [];
            if (priceMatches.length >= 1) salePrice = priceMatches[0];
            if (priceMatches.length >= 2) origPrice = priceMatches[1];

            // Find popularity: "Popularity: X/5"
            let popularity = '';
            for (const line of lines) {
                const pm = line.match(/Popularity:\\s*(\\d+\\/\\d+)/);
                if (pm) { popularity = pm[1]; break; }
            }

            items.push({product_name: title, store, sale_price: salePrice, original_price: origPrice, popularity});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = DealItem()
        item.product_name = d.get("product_name", "")
        item.store = d.get("store", "")
        item.sale_price = d.get("sale_price", "")
        item.original_price = d.get("original_price", "")
        item.popularity = d.get("popularity", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} deals in '{request.category}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.product_name}")
        print(f"     Store: {item.store}  Price: {item.sale_price} (was {item.original_price})")
        print(f"     Popularity: {item.popularity}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("dealnews")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = browse_dealnews(page, DealNewsBrowseRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} deals")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
