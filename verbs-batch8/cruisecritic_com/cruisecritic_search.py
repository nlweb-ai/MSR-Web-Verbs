"""
Auto-generated Playwright script (Python)
Cruise Critic – Search for cruise deals by keyword
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CruisecriticSearchRequest:
    search_query: str = "Caribbean"
    max_results: int = 5


@dataclass
class CruisecriticDealItem:
    cruise_line: str = ""
    ship_name: str = ""
    destination: str = ""
    duration: str = ""
    departure_date: str = ""
    price_from: str = ""
    rating: str = ""


@dataclass
class CruisecriticSearchResult:
    items: List[CruisecriticDealItem] = field(default_factory=list)


# Search for cruise deals on Cruise Critic by keyword.
def cruisecritic_search(page: Page, request: CruisecriticSearchRequest) -> CruisecriticSearchResult:
    """Search for cruise deals on Cruise Critic."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://www.cruisecritic.com/cruiseto/cruiseitineraries.cfm?deession=Caribbean"
    print(f"Loading {url}...")
    checkpoint("Navigate to Cruise Critic search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = CruisecriticSearchResult()

    checkpoint("Extract cruise deal listings")
    js_code = """(max) => {
        const cards = document.querySelectorAll('article, [class*="search-result"], [class*="Result"], [class*="card"], [class*="listing"], [class*="cruise"]');
        const items = [];
        for (const card of cards) {
            if (items.length >= max) break;
            const lineEl = card.querySelector('[class*="cruise-line"], [class*="line-name"], [class*="brand"]');
            const shipEl = card.querySelector('[class*="ship-name"], [class*="ship"], h3, h2');
            const destEl = card.querySelector('[class*="destination"], [class*="itinerary"], [class*="region"]');
            const durEl = card.querySelector('[class*="duration"], [class*="nights"], [class*="length"]');
            const dateEl = card.querySelector('[class*="date"], [class*="departure"], time');
            const priceEl = card.querySelector('[class*="price"], [class*="cost"], [class*="fare"]');
            const ratingEl = card.querySelector('[class*="rating"], [class*="score"], [class*="stars"]');

            const cruise_line = lineEl ? lineEl.textContent.trim() : '';
            const ship_name = shipEl ? shipEl.textContent.trim() : '';
            const destination = destEl ? destEl.textContent.trim() : '';
            const duration = durEl ? durEl.textContent.trim() : '';
            const departure_date = dateEl ? (dateEl.getAttribute('datetime') || dateEl.textContent.trim()) : '';
            const price_from = priceEl ? priceEl.textContent.trim() : '';
            const rating = ratingEl ? ratingEl.textContent.trim() : '';

            if (ship_name || cruise_line) {
                items.push({cruise_line, ship_name, destination, duration, departure_date, price_from, rating});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = CruisecriticDealItem()
        item.cruise_line = d.get("cruise_line", "")
        item.ship_name = d.get("ship_name", "")
        item.destination = d.get("destination", "")
        item.duration = d.get("duration", "")
        item.departure_date = d.get("departure_date", "")
        item.price_from = d.get("price_from", "")
        item.rating = d.get("rating", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Cruise {i}:")
        print(f"    Line:      {item.cruise_line}")
        print(f"    Ship:      {item.ship_name}")
        print(f"    Dest:      {item.destination}")
        print(f"    Duration:  {item.duration}")
        print(f"    Departure: {item.departure_date}")
        print(f"    Price:     {item.price_from}")
        print(f"    Rating:    {item.rating}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("cruisecritic")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = CruisecriticSearchRequest()
            result = cruisecritic_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} cruise deals")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
