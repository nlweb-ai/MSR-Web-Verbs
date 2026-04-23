import os
import sys
import shutil
from dataclasses import dataclass, field
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class TimeoutSearchRequest:
    search_query: str = "restaurants New York"
    max_results: int = 5


@dataclass
class TimeoutListingItem:
    title: str = ""
    venue_name: str = ""
    category: str = ""
    location: str = ""
    summary: str = ""
    rating: str = ""


@dataclass
class TimeoutSearchResult:
    listings: List[TimeoutListingItem] = field(default_factory=list)
    error: str = ""


def timeout_search(page, request: TimeoutSearchRequest) -> TimeoutSearchResult:
    result = TimeoutSearchResult()
    try:
        url = f"https://www.timeout.com/search?q={request.search_query}"
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)

        checkpoint("Search results loaded")

        listings_data = page.evaluate("""() => {
            const listings = [];
            const items = document.querySelectorAll('article, [class*="result"], [class*="card"], [class*="listing"]');
            for (const item of items) {
                const titleEl = item.querySelector('h2, h3, [class*="title"], a[class*="heading"]');
                const venueEl = item.querySelector('[class*="venue"], [class*="name"]');
                const categoryEl = item.querySelector('[class*="category"], [class*="label"], [class*="tag"]');
                const locationEl = item.querySelector('[class*="location"], [class*="address"], [class*="neighborhood"]');
                const summaryEl = item.querySelector('p, [class*="excerpt"], [class*="description"], [class*="summary"]');
                const ratingEl = item.querySelector('[class*="rating"], [class*="score"], [class*="stars"]');
                listings.push({
                    title: titleEl ? titleEl.textContent.trim() : '',
                    venue_name: venueEl ? venueEl.textContent.trim() : '',
                    category: categoryEl ? categoryEl.textContent.trim() : '',
                    location: locationEl ? locationEl.textContent.trim() : '',
                    summary: summaryEl ? summaryEl.textContent.trim() : '',
                    rating: ratingEl ? ratingEl.textContent.trim() : '',
                });
            }
            return listings;
        }""")

        for item in listings_data[:request.max_results]:
            result.listings.append(TimeoutListingItem(**item))

        checkpoint(f"Extracted {len(result.listings)} listings")

    except Exception as e:
        result.error = str(e)
    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir()
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(ws_url)
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()

    try:
        request = TimeoutSearchRequest()
        result = timeout_search(page, request)
        print(f"Found {len(result.listings)} listings")
        for i, l in enumerate(result.listings):
            print(f"  {i+1}. {l.title} at {l.venue_name} ({l.location}) - {l.rating}")
        if result.error:
            print(f"Error: {result.error}")
    finally:
        browser.close()
        pw.stop()
        chrome_proc.terminate()
        shutil.rmtree(profile_dir, ignore_errors=True)


def run_with_debugger():
    test_func()


if __name__ == "__main__":
    run_with_debugger()
