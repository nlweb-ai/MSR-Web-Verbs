"""
Playwright script (Python) — Booking.com Attractions
Search for attractions on Booking.com.
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
class BookingAttractionsRequest:
    location: str = "Paris, France"
    max_results: int = 5


@dataclass
class AttractionItem:
    name: str = ""
    price: str = ""
    rating: str = ""
    num_reviews: str = ""
    duration: str = ""


@dataclass
class BookingAttractionsResult:
    location: str = ""
    items: List[AttractionItem] = field(default_factory=list)


def search_booking_attractions(page: Page, request: BookingAttractionsRequest) -> BookingAttractionsResult:
    """Search Booking.com for attractions."""
    city = request.location.split(",")[0].strip().lower()
    country_map = {"france": "fr", "italy": "it", "spain": "es", "germany": "de", "uk": "gb", "united kingdom": "gb", "japan": "jp", "united states": "us"}
    country = request.location.split(",")[1].strip().lower() if "," in request.location else ""
    cc = country_map.get(country, country[:2] if country else "")
    url = f"https://www.booking.com/attractions/searchresults/{cc}/{city}.html"
    print(f"Loading {url}...")
    checkpoint("Navigate to attractions")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = BookingAttractionsResult(location=request.location)

    checkpoint("Extract attractions")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('[data-testid*="card"], [class*="attraction"], [class*="product-card"], article, [class*="ActivityCard"]');
        for (const card of cards) {
            if (items.length >= max) break;
            const text = (card.textContent || '').replace(/\\s+/g, ' ').trim();

            let name = '';
            const nameEl = card.querySelector('h3, h4, [class*="title"], [data-testid*="title"]');
            if (nameEl) name = nameEl.textContent.trim();
            if (!name || name.length < 3) continue;
            if (items.some(i => i.name === name)) continue;

            let price = '';
            const priceMatch = text.match(/(?:US)?\\$[\\d,.]+|\u20ac[\\d,.]+/i);
            if (priceMatch) price = priceMatch[0];

            let rating = '';
            const ratingMatch = text.match(/(\\d+\\.\\d+)\\s*(?:\\/|out of|star|review)/i);
            if (ratingMatch) rating = ratingMatch[1];

            let reviews = '';
            const revMatch = text.match(/(\\d[\\d,]*)\\s*(?:review|rating)/i);
            if (revMatch) reviews = revMatch[1];

            let duration = '';
            const durMatch = text.match(/(\\d+\\s*(?:hour|hr|min|day)s?)/i);
            if (durMatch) duration = durMatch[0];

            items.push({name: name, price: price, rating: rating, num_reviews: reviews, duration: duration});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = AttractionItem()
        item.name = d.get("name", "")
        item.price = d.get("price", "")
        item.rating = d.get("rating", "")
        item.num_reviews = d.get("num_reviews", "")
        item.duration = d.get("duration", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} attractions in '{request.location}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name}")
        print(f"     Price: {item.price}  Rating: {item.rating}  Reviews: {item.num_reviews}  Duration: {item.duration}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("booking_attr")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_booking_attractions(page, BookingAttractionsRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} attractions")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
