"""
Playwright script (Python) — OpenTable Restaurant Search
Search OpenTable for Italian restaurants in NYC.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class OpenTableRequest:
    location: str = "New York City"
    cuisine: str = "Italian"
    max_results: int = 5


@dataclass
class RestaurantItem:
    name: str = ""
    cuisine: str = ""
    price_range: str = ""
    rating: str = ""
    num_reviews: str = ""
    next_available: str = ""


@dataclass
class OpenTableResult:
    restaurants: List[RestaurantItem] = field(default_factory=list)


# Searches OpenTable for restaurants and extracts name, cuisine,
# price range, rating, reviews, and next available time.
def search_opentable(page: Page, request: OpenTableRequest) -> OpenTableResult:
    url = "https://www.opentable.com/s?covers=2&dateTime=2025-04-20T19%3A00&term=Italian&metroId=4"
    print(f"Loading {url}...")
    checkpoint("Navigate to OpenTable search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)

    result = OpenTableResult()

    checkpoint("Extract restaurant listings")
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find start: line containing 'restaurants match'
        let start = 0;
        for (let i = 0; i < lines.length; i++) {
            if (/restaurants match/i.test(lines[i])) { start = i + 1; break; }
        }
        // Parse restaurant blocks: Name, RatingText, (count), price, cuisine+location, ...
        const ratingWords = ['Exceptional', 'Awesome', 'Great', 'Good'];
        for (let i = start; i < lines.length && results.length < max; i++) {
            // Check if next line is a rating word (indicates this line is a restaurant name)
            if (i + 1 < lines.length && ratingWords.some(w => lines[i + 1] === w)) {
                const name = lines[i];
                const rating = lines[i + 1] || '';
                const num_reviews = (lines[i + 2] || '').replace(/[()]/g, '');
                const price_range = lines[i + 3] || '';
                // cuisine+location line like "· Italian · North Beach"
                const cuisineLine = lines[i + 4] || '';
                const cuisine = cuisineLine.replace(/^[^a-zA-Z]*/, '').trim();
                // Look for time slots after "Booked X times today" or availability line
                let next_available = '';
                for (let j = i + 5; j < Math.min(i + 10, lines.length); j++) {
                    if (/^\\d{1,2}:\\d{2}\\s*(AM|PM)/i.test(lines[j])) {
                        next_available = lines[j].replace(/\\*$/, '');
                        break;
                    }
                }
                results.push({ name, cuisine, price_range, rating, num_reviews, next_available });
                i += 5; // skip past this block
            }
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = RestaurantItem()
        item.name = d.get("name", "")
        item.cuisine = d.get("cuisine", "")
        item.price_range = d.get("price_range", "")
        item.rating = d.get("rating", "")
        item.num_reviews = d.get("num_reviews", "")
        item.next_available = d.get("next_available", "")
        result.restaurants.append(item)

    print(f"\nFound {len(result.restaurants)} restaurants:")
    for i, r in enumerate(result.restaurants, 1):
        print(f"\n  {i}. {r.name}")
        print(f"     Rating: {r.rating} ({r.num_reviews})  Price: {r.price_range}  Cuisine: {r.cuisine}  Next: {r.next_available}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("opentable")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_opentable(page, OpenTableRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.restaurants)} restaurants")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
