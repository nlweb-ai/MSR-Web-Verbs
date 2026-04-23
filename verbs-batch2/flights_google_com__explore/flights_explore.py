"""
Playwright script (Python) — Google Flights Explore
Find cheap flight destinations from a departure city using the explore map view.

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class FlightsExploreRequest:
    departure_city: str
    depart_date: date
    return_date: date
    max_results: int


@dataclass(frozen=True)
class FlightDestination:
    city: str
    price: str


@dataclass(frozen=True)
class FlightsExploreResult:
    departure_city: str
    depart_date: date
    return_date: date
    destinations: list[FlightDestination]


# Navigates to Google Flights Explore, sets a departure city, and extracts
# up to max_results cheap destinations with city name and round-trip price.
def explore_flights(
    page: Page,
    request: FlightsExploreRequest,
) -> FlightsExploreResult:
    departure_city = request.departure_city
    depart_date = request.depart_date
    return_date = request.return_date
    max_results = request.max_results
    trip_days = (return_date - depart_date).days

    print(f"  Departure: {departure_city}")
    print(f"  Trip: {trip_days} days")
    print(f"  Max results: {max_results}\n")

    results: list[FlightDestination] = []

    try:
        # ── Navigate ──────────────────────────────────────────────────────
        print("Loading Google Flights Explore...")
        checkpoint("Navigate to https://www.google.com/travel/flights/explore")
        page.goto("https://www.google.com/travel/flights/explore")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # ── STEP 1: Enter departure city ──────────────────────────────────
        print(f'STEP 1: Set departure city to "{departure_city}"...')

        # The departure input is: input[aria-label="Where from?"]
        dep_input = page.locator('input[aria-label="Where from?"]')
        dep_input.wait_for(state="visible", timeout=5000)

        checkpoint(f"Will set departure to: {departure_city} (type + auto-select)")

        # Use focus() to avoid scroll-jumping, then type and immediately
        # click the first suggestion — no checkpoint in between, because
        # the checkpoint dialog steals browser focus and closes the dropdown.
        dep_input.focus()
        page.wait_for_timeout(500)
        page.keyboard.press("Control+a")
        page.keyboard.press("Backspace")
        page.wait_for_timeout(300)
        page.keyboard.type(departure_city, delay=80)
        print(f'  Typed "{departure_city}"')
        page.wait_for_timeout(2000)

        # Click the first autocomplete suggestion immediately (no checkpoint).
        # Use aria-label filter to avoid matching hidden options from other
        # comboboxes ("Where to?", "Where else?") earlier in the DOM.
        selected_suggestion = False
        try:
            suggestion = page.locator(
                f'li[role="option"][aria-label*="{departure_city}" i]'
            ).first
            suggestion.wait_for(state="visible", timeout=3000)
            label = suggestion.get_attribute("aria-label")
            suggestion.evaluate("el => el.click()")
            print(f'  Clicked suggestion: "{label}"')
            selected_suggestion = True
        except Exception:
            page.keyboard.press("Enter")
            print("  No suggestion found, pressed Enter")
        page.wait_for_timeout(1000)

        # Verify what the input now shows
        current_value = dep_input.evaluate("el => el.value")
        print(f'  Departure field now shows: "{current_value}"')
        checkpoint(f"Departure set to: {current_value} (clicked={'yes' if selected_suggestion else 'no, used Enter'})")

        # ── STEP 2: Wait for explore map ──────────────────────────────────
        print("STEP 2: Waiting for explore map to load...")
        page.wait_for_timeout(2000)

        # ── STEP 3: Extract destinations ──────────────────────────────────
        print(f"STEP 3: Extract up to {max_results} cheap destinations...")
        page.wait_for_timeout(2000)

        h3s = page.locator("h3")
        count = h3s.count()
        print(f"  Found {count} destination headings")

        for i in range(count):
            if len(results) >= max_results:
                break
            h3 = h3s.nth(i)
            try:
                city = h3.inner_text(timeout=2000).strip()
                card_text = h3.evaluate(
                    "el => el.parentElement.parentElement.innerText"
                )
                price_match = re.search(r"\$\d[\d,]*", card_text)
                price = price_match.group(0) if price_match else "N/A"

                if city:
                    results.append(FlightDestination(
                        city=city,
                        price=price,
                    ))
                    print(f"  {len(results)}. {city} | {price}")
            except Exception as e:
                print(f"  Error on item {i}: {e}")
                continue

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nFound {len(results)} cheap destinations from {departure_city}:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.city} — {r.price}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return FlightsExploreResult(
        departure_city=departure_city,
        depart_date=depart_date,
        return_date=return_date,
        destinations=results,
    )


def test_explore_flights() -> None:
    today = date.today()
    depart_date = today + relativedelta(months=1)
    return_date = depart_date + timedelta(days=5)

    request = FlightsExploreRequest(
        departure_city="Chicago",
        depart_date=depart_date,
        return_date=return_date,
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
            result = explore_flights(page, request)
            assert result.departure_city == request.departure_city
            assert len(result.destinations) <= request.max_results
            print(f"\nTotal destinations found: {len(result.destinations)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_explore_flights)
