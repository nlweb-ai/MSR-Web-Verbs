"""
Playwright script (Python) — TripAdvisor Hotel Search
Search for hotels by destination and extract name, price, and rating.

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
import urllib.parse
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class TripAdvisorHotelsRequest:
    destination: str
    max_results: int


@dataclass(frozen=True)
class TripAdvisorHotel:
    name: str
    price: str
    rating: str


@dataclass(frozen=True)
class TripAdvisorHotelsResult:
    destination: str
    hotels: list[TripAdvisorHotel]


# Searches TripAdvisor for hotels at a destination (via Google) and extracts
# up to max_results hotels with name, price, and rating.
def search_tripadvisor_hotels(
    page: Page,
    request: TripAdvisorHotelsRequest,
) -> TripAdvisorHotelsResult:
    destination = request.destination
    max_results = request.max_results

    print(f"  Destination: {destination}\n")

    results: list[TripAdvisorHotel] = []

    try:
        google_q = urllib.parse.quote(f"site:tripadvisor.com Hotels {destination}")
        google_url = f"https://www.google.com/search?q={google_q}"
        checkpoint(f"Navigate to {google_url}")
        page.goto(google_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        links = page.locator('a[href*="tripadvisor.com/Hotels-"]')
        lc = links.count()
        if lc > 0:
            href = links.first.get_attribute("href", timeout=5000)
            if href:
                checkpoint(f"Navigate to TripAdvisor hotels page")
                page.goto(href)
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(6000)
                if page.title() == "tripadvisor.com":
                    page.reload()
                    page.wait_for_load_state("domcontentloaded")
                    page.wait_for_timeout(6000)

        body = page.locator("body").inner_text(timeout=5000)
        lines = [l.strip() for l in body.split("\n") if l.strip()]
        i = 0
        while i < len(lines) and len(results) < max_results:
            if i + 2 < len(lines) and re.match(r'^\d\.\d$', lines[i + 1]) and "reviews" in lines[i + 2].lower():
                name = lines[i]
                rating = lines[i + 1] + " " + lines[i + 2]
                price = "N/A"
                if i + 4 < len(lines) and lines[i + 3].lower() == "from" and "$" in lines[i + 4]:
                    price = lines[i + 4]
                results.append(TripAdvisorHotel(name=name, price=price, rating=rating))
                print(f"  {len(results)}. {name} | {price} | {rating}")
                i += 5
            else:
                i += 1

        print(f"\nFound {len(results)} hotels:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name} — {r.price} ({r.rating})")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return TripAdvisorHotelsResult(destination=destination, hotels=results)


def test_search_tripadvisor_hotels() -> None:
    request = TripAdvisorHotelsRequest(destination="San Diego", max_results=5)
    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir, channel="chrome", headless=False, viewport=None,
            args=["--disable-blink-features=AutomationControlled", "--disable-infobars", "--disable-extensions"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_tripadvisor_hotels(page, request)
            assert result.destination == request.destination
            assert len(result.hotels) <= request.max_results
            print(f"\nTotal hotels found: {len(result.hotels)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_tripadvisor_hotels)
