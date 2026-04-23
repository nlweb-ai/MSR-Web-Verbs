"""
Playwright script (Python) — AutoTrader Search
Search for used cars on AutoTrader.
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
class AutoTraderSearchRequest:
    make_model: str = "Honda Civic"
    max_price: int = 25000
    zip_code: str = "60601"
    radius: int = 50
    max_results: int = 5


@dataclass
class CarItem:
    title: str = ""
    mileage: str = ""
    price: str = ""
    dealer_name: str = ""


@dataclass
class AutoTraderSearchResult:
    query: str = ""
    items: List[CarItem] = field(default_factory=list)


def search_autotrader(page: Page, request: AutoTraderSearchRequest) -> AutoTraderSearchResult:
    """Search AutoTrader for used cars."""
    make = request.make_model.split()[0].lower()
    model = request.make_model.split()[1].lower() if len(request.make_model.split()) > 1 else ""
    url = f"https://www.autotrader.com/cars-for-sale/used/{make}/{model}/{request.zip_code}?searchRadius={request.radius}&priceRange-max={request.max_price}"
    print(f"Loading {url}...")
    checkpoint("Navigate to listings")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = AutoTraderSearchResult(query=request.make_model)

    checkpoint("Extract car listings")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();
        const cards = document.querySelectorAll('[data-cmp="inventoryListing"], [class*="inventory-listing"]');
        for (const card of cards) {
            if (items.length >= max) break;
            const lines = card.innerText.split('\\n').map(l => l.trim()).filter(l => l);

            let title = '';
            let trim = '';
            for (let li = 0; li < lines.length; li++) {
                const tm = lines[li].match(/^(\\d{4}\\s+.+)/);
                if (tm) {
                    title = tm[1];
                    if (li + 1 < lines.length && lines[li+1].length < 20 && !lines[li+1].match(/\\d+K?\\s*mi/i) && !lines[li+1].match(/^[\\d,]+$/)) {
                        trim = lines[li+1];
                    }
                    break;
                }
            }
            if (!title) continue;
            const fullTitle = trim ? title + ' ' + trim : title;
            if (seen.has(fullTitle)) continue;
            seen.add(fullTitle);

            let mileage = '';
            for (const line of lines) {
                const mm = line.match(/^(\\d+K?\\s*mi)$/i);
                if (mm) { mileage = mm[1]; break; }
            }

            let price = '';
            for (const line of lines) {
                const pm = line.match(/^([\\d,]+)$/);
                if (pm && pm[1].length >= 4) { price = '$' + pm[1]; break; }
            }

            let dealer = '';
            for (const line of lines) {
                const dm = line.match(/(?:Sponsored )?by\\s+(.+)/i);
                if (dm) { dealer = dm[1]; break; }
            }

            items.push({title: fullTitle, mileage, price, dealer_name: dealer});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = CarItem()
        item.title = d.get("title", "")
        item.mileage = d.get("mileage", "")
        item.price = d.get("price", "")
        item.dealer_name = d.get("dealer_name", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} listings for '{request.make_model}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Price: {item.price}  Mileage: {item.mileage}  Dealer: {item.dealer_name}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("autotrader")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_autotrader(page, AutoTraderSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} listings")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
