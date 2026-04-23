"""
Rover – Search for pet sitters by location

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
class RoverSearchRequest:
    location: str = "Seattle, WA"
    max_results: int = 5


@dataclass
class RoverSitterItem:
    sitter_name: str = ""
    rating: str = ""
    num_reviews: str = ""
    price_per_night: str = ""
    services_offered: str = ""
    distance: str = ""
    response_time: str = ""


@dataclass
class RoverSearchResult:
    items: List[RoverSitterItem] = field(default_factory=list)


# Search for pet sitters on Rover by location.
def rover_search(page: Page, request: RoverSearchRequest) -> RoverSearchResult:
    """Search for pet sitters on Rover."""
    print(f"  Location: {request.location}\n")

    location = request.location.replace(" ", "+")
    url = f"https://www.rover.com/search/?location={location}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Rover search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = RoverSearchResult()

    checkpoint("Extract sitter listings")
    js_code = """(max) => {
        const cards = document.querySelectorAll('[class*="SearchResult"], [class*="search-result"], [class*="SitterCard"], [class*="sitter-card"], [class*="Card"], [data-testid*="search-result"]');
        const items = [];
        for (const card of cards) {
            if (items.length >= max) break;
            const nameEl = card.querySelector('h2, h3, [class*="name"], [class*="title"], [data-testid*="name"]');
            const ratingEl = card.querySelector('[class*="rating"], [class*="score"], [class*="stars"]');
            const reviewsEl = card.querySelector('[class*="review"], [class*="Reviews"]');
            const priceEl = card.querySelector('[class*="price"], [class*="cost"], [class*="rate"]');
            const servicesEl = card.querySelector('[class*="service"], [class*="badge"], [class*="tag"]');
            const distEl = card.querySelector('[class*="distance"], [class*="miles"], [class*="dist"]');
            const responseEl = card.querySelector('[class*="response"], [class*="reply"]');

            const sitter_name = nameEl ? nameEl.textContent.trim() : '';
            const rating = ratingEl ? ratingEl.textContent.trim() : '';
            const num_reviews = reviewsEl ? reviewsEl.textContent.trim().replace(/[^0-9]/g, '') : '';
            const price_per_night = priceEl ? priceEl.textContent.trim() : '';
            const services_offered = servicesEl ? servicesEl.textContent.trim() : '';
            const distance = distEl ? distEl.textContent.trim() : '';
            const response_time = responseEl ? responseEl.textContent.trim() : '';

            if (sitter_name) {
                items.push({sitter_name, rating, num_reviews, price_per_night, services_offered, distance, response_time});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = RoverSitterItem()
        item.sitter_name = d.get("sitter_name", "")
        item.rating = d.get("rating", "")
        item.num_reviews = d.get("num_reviews", "")
        item.price_per_night = d.get("price_per_night", "")
        item.services_offered = d.get("services_offered", "")
        item.distance = d.get("distance", "")
        item.response_time = d.get("response_time", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Sitter {i}:")
        print(f"    Name:      {item.sitter_name}")
        print(f"    Rating:    {item.rating}")
        print(f"    Reviews:   {item.num_reviews}")
        print(f"    Price:     {item.price_per_night}")
        print(f"    Services:  {item.services_offered}")
        print(f"    Distance:  {item.distance}")
        print(f"    Response:  {item.response_time}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("rover")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = RoverSearchRequest()
            result = rover_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} sitters")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
