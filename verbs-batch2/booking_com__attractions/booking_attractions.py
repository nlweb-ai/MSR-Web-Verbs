"""
Playwright script (Python) — Booking.com Attractions Search
Search for attractions in a city and extract name, rating, and price.

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BookingAttractionsRequest:
    city: str
    max_results: int


@dataclass(frozen=True)
class BookingAttraction:
    name: str
    rating: str
    price: str


@dataclass(frozen=True)
class BookingAttractionsResult:
    city: str
    attractions: list[BookingAttraction]


# Searches Booking.com Attractions for a given city and extracts up to
# max_results attractions with name, rating, and price.
def search_booking_attractions(
    page: Page,
    request: BookingAttractionsRequest,
) -> BookingAttractionsResult:
    city = request.city
    max_results = request.max_results

    print(f"  City: {city}")
    print(f"  Max results: {max_results}\n")

    results: list[BookingAttraction] = []

    try:
        # ── Navigate ──────────────────────────────────────────────────────
        print("Loading Booking.com Attractions...")
        checkpoint("Navigate to https://www.booking.com/attractions")
        page.goto("https://www.booking.com/attractions")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        # ── Dismiss popups / cookie banners ───────────────────────────────
        for selector in [
            "button#onetrust-accept-btn-handler",
            "[aria-label='Dismiss sign-in info.']",
            "button:has-text('Accept')",
            "button:has-text('Got it')",
        ]:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {selector}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        # ── STEP 1: Search for attractions ────────────────────────────────
        print(f'STEP 1: Search for attractions in "{city}"...')

        search_input = page.locator('[data-testid="search-input-field"]').first
        checkpoint("Click search input")
        search_input.evaluate("el => el.click()")
        page.wait_for_timeout(500)
        page.keyboard.press("Control+a")
        checkpoint(f"Type city: {city}")
        search_input.fill(city)
        page.wait_for_timeout(2000)

        # Try to select first autocomplete suggestion
        try:
            suggestion = page.locator('[data-testid="search-bar-result"]').first
            suggestion.wait_for(state="visible", timeout=5000)
            checkpoint("Click first autocomplete suggestion")
            suggestion.evaluate("el => el.click()")
            print(f"  Selected first suggestion for \"{city}\"")
            page.wait_for_timeout(2000)
        except Exception:
            print("  No autocomplete suggestion found")

        # Click the search button
        search_btn = page.locator('[data-testid="search-button"]').first
        checkpoint("Click Search button")
        search_btn.evaluate("el => el.click()")
        print("  Clicked Search button")
        page.wait_for_timeout(2000)

        # Wait for results page to load
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)
        print(f"  URL: {page.url}")

        # ── STEP 2: Extract attractions ───────────────────────────────────
        print(f"STEP 2: Extract up to {max_results} attractions...")

        cards = page.locator('[data-testid="card"]')
        count = cards.count()
        print(f"  Found {count} attraction cards")

        for i in range(min(count, max_results)):
            card = cards.nth(i)
            try:
                # Name
                name = "N/A"
                try:
                    name_el = card.locator('[data-testid="card-title"]').first
                    name = name_el.inner_text(timeout=2000).strip()
                except Exception:
                    pass

                # Rating
                rating = "N/A"
                try:
                    review_el = card.locator('[data-testid="review-score"]').first
                    review_text = review_el.inner_text(timeout=2000).strip()
                    m = re.search(r"(\d+(?:\.\d+)?)\s+out\s+of\s+10", review_text)
                    if m:
                        rating = m.group(1)
                    else:
                        m2 = re.search(r"\n(\d+(?:\.\d+)?)\n", review_text)
                        if m2:
                            rating = m2.group(1)
                except Exception:
                    pass

                # Price
                price = "N/A"
                try:
                    price_el = card.locator('[data-testid="price"]').first
                    price_text = price_el.inner_text(timeout=2000).strip()
                    m = re.search(r"(US?\$[\d,.]+|€[\d,.]+|£[\d,.]+)", price_text)
                    if m:
                        price = m.group(1)
                except Exception:
                    pass

                results.append(BookingAttraction(
                    name=name,
                    rating=rating,
                    price=price,
                ))

            except Exception as e:
                print(f"  Skipping card {i + 1}: {e}")

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nResults for attractions in '{city}':")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name}")
            print(f"     Rating: {r.rating}")
            print(f"     Price:  {r.price}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return BookingAttractionsResult(
        city=city,
        attractions=results,
    )


def test_search_booking_attractions() -> None:
    request = BookingAttractionsRequest(
        city="Paris",
        max_results=5,
    )

    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=False,
            viewport=None,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_booking_attractions(page, request)
            assert result.city == request.city
            assert len(result.attractions) <= request.max_results
            print(f"\nTotal attractions found: {len(result.attractions)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_booking_attractions)
