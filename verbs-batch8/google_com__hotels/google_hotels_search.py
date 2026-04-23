"""
Google Hotels – Search for hotel listings

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
class GoogleHotelsSearchRequest:
    destination: str = "San Francisco"
    max_results: int = 5


@dataclass
class GoogleHotelItem:
    hotel_name: str = ""
    price_per_night: str = ""
    rating: str = ""
    num_reviews: str = ""
    amenities: str = ""
    distance_from_center: str = ""


@dataclass
class GoogleHotelsSearchResult:
    items: List[GoogleHotelItem] = field(default_factory=list)


# Search for hotel listings on Google Hotels.
def google_hotels_search(page: Page, request: GoogleHotelsSearchRequest) -> GoogleHotelsSearchResult:
    """Search for hotel listings on Google Hotels."""
    print(f"  Destination: {request.destination}")
    print(f"  Max results: {request.max_results}\n")

    dest_encoded = request.destination.replace(" ", "+")
    url = f"https://www.google.com/travel/hotels/{request.destination}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Google Hotels search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = GoogleHotelsSearchResult()

    checkpoint("Extract hotel listings")
    js_code = """(max) => {
        const cards = document.querySelectorAll('[class*="property"], [class*="hotel"], [class*="result"], [data-hveid], [jsaction*="hotel"]');
        const items = [];
        for (const card of cards) {
            if (items.length >= max) break;
            const nameEl = card.querySelector('h2, h3, [class*="name"], [class*="title"], [class*="Name"]');
            const priceEl = card.querySelector('[class*="price"], [class*="Price"], [class*="cost"]');
            const ratingEl = card.querySelector('[class*="rating"], [class*="Rating"], [aria-label*="star"], [aria-label*="rated"]');
            const reviewsEl = card.querySelector('[class*="review"], [class*="Review"], [class*="count"]');
            const amenitiesEl = card.querySelector('[class*="amenit"], [class*="Amenit"], [class*="feature"]');
            const distanceEl = card.querySelector('[class*="distance"], [class*="Distance"], [class*="location"]');

            const hotel_name = nameEl ? nameEl.textContent.trim() : '';
            const price_per_night = priceEl ? priceEl.textContent.trim() : '';
            const rating = ratingEl ? ratingEl.textContent.trim() : '';
            const num_reviews = reviewsEl ? reviewsEl.textContent.trim() : '';
            const amenities = amenitiesEl ? amenitiesEl.textContent.trim() : '';
            const distance_from_center = distanceEl ? distanceEl.textContent.trim() : '';

            if (hotel_name) {
                items.push({hotel_name, price_per_night, rating, num_reviews, amenities, distance_from_center});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = GoogleHotelItem()
        item.hotel_name = d.get("hotel_name", "")
        item.price_per_night = d.get("price_per_night", "")
        item.rating = d.get("rating", "")
        item.num_reviews = d.get("num_reviews", "")
        item.amenities = d.get("amenities", "")
        item.distance_from_center = d.get("distance_from_center", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Hotel {i}:")
        print(f"    Name:     {item.hotel_name}")
        print(f"    Price:    {item.price_per_night}")
        print(f"    Rating:   {item.rating}")
        print(f"    Reviews:  {item.num_reviews}")
        print(f"    Amenities:{item.amenities[:60]}")
        print(f"    Distance: {item.distance_from_center}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("google_hotels")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = GoogleHotelsSearchRequest()
            result = google_hotels_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} hotel listings")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
