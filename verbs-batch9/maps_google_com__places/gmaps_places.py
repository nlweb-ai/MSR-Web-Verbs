"""
Playwright script (Python) — Google Maps Places Search
Search Google Maps for places and extract details.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GMapsRequest:
    search_query: str = "coffee shops near Times Square, New York"
    max_results: int = 5


@dataclass
class PlaceItem:
    name: str = ""
    rating: str = ""
    address: str = ""


@dataclass
class GMapsResult:
    query: str = ""
    places: List[PlaceItem] = field(default_factory=list)


# Searches Google Maps for places matching the query and returns
# up to max_results places with name, rating, and address.
def search_gmaps_places(page: Page, request: GMapsRequest) -> GMapsResult:
    import urllib.parse
    url = f"https://www.google.com/maps/search/{urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Google Maps search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)

    result = GMapsResult(query=request.search_query)

    checkpoint("Extract place listings")
    js_code = """(max) => {
        const results = [];
        const feed = document.querySelector('[role="feed"]');
        if (!feed) return results;
        const items = feed.querySelectorAll(':scope > div');
        const seen = new Set();
        for (const item of items) {
            if (results.length >= max) break;
            const link = item.querySelector('a[aria-label]');
            if (!link) continue;
            const name = link.getAttribute('aria-label');
            if (!name || name.length < 2 || seen.has(name)) continue;
            seen.add(name);
            const lines = item.innerText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            let rating = '', address = '';
            // Rating is usually a short line like "4.1" or "4.5"
            for (const line of lines) {
                if (/^\\d\\.\\d$/.test(line)) { rating = line; continue; }
                // Address line contains the street info (has digits + letters)
                if (!address && /\\d/.test(line) && /[A-Za-z]/.test(line) && line.length > 5 && line.length < 80) {
                    // Skip lines that are hours or status
                    if (/Open|Closed|Closes|Opens|hours/i.test(line)) continue;
                    if (/Order|Dine|Delivery|Pickup/i.test(line)) continue;
                    // Address often has · separators like "Coffee shop · $$ · 11 Times Sq"
                    const parts = line.split('·').map(p => p.trim());
                    // Last part with numbers is likely address
                    for (let k = parts.length - 1; k >= 0; k--) {
                        if (/\\d/.test(parts[k]) && parts[k].length > 3) { address = parts[k]; break; }
                    }
                }
            }
            results.push({ name, rating, address });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = PlaceItem()
        item.name = d.get("name", "")
        item.rating = d.get("rating", "")
        item.address = d.get("address", "")
        result.places.append(item)

    print(f"\nFound {len(result.places)} places for '{request.search_query}':")
    for i, item in enumerate(result.places, 1):
        print(f"\n  {i}. {item.name}")
        print(f"     Rating: {item.rating}  Address: {item.address}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("gmaps")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_gmaps_places(page, GMapsRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.places)} places")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
