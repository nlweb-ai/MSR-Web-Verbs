"""
Playwright script (Python) — AutoTrader.com Used Car Search
Make: Toyota  Model: Camry
ZIP: 60601  Radius: 50 miles
Max results: 5

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
class AutotraderSearchRequest:
    make: str
    model: str
    zip_code: str
    radius_miles: int
    max_results: int


@dataclass(frozen=True)
class AutotraderListing:
    year_make_model: str
    price: str
    mileage: str
    dealer: str


@dataclass(frozen=True)
class AutotraderSearchResult:
    make: str
    model: str
    zip_code: str
    radius_miles: int
    listings: list[AutotraderListing]


# Searches AutoTrader for used cars matching the given make, model, zip code, and radius,
# then returns up to max_results listings with year/make/model, price, mileage, and dealer.
def search_autotrader_listings(
    page: Page,
    request: AutotraderSearchRequest,
) -> AutotraderSearchResult:
    make = request.make
    model = request.model
    zip_code = request.zip_code
    radius_miles = request.radius_miles
    max_results = request.max_results

    print(f"  Make: {make}  Model: {model}")
    print(f"  ZIP: {zip_code}  Radius: {radius_miles} miles")
    print(f"  Max results: {max_results}\n")

    results: list[AutotraderListing] = []

    try:
        # ── Navigate to search results ────────────────────────────────────
        make_lower = make.lower()
        model_lower = model.lower()
        search_url = (
            f"https://www.autotrader.com/cars-for-sale/used-cars/{make_lower}/{model_lower}"
            f"?zip={zip_code}&searchRadius={radius_miles}"
        )
        print(f"Loading {search_url}...")
        checkpoint(f"Navigate to {search_url}")
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)
        try:
            page.locator('div[data-cmp="inventoryListing"]').first.wait_for(state="visible", timeout=15000)
        except Exception:
            pass
        page.wait_for_timeout(2000)
        print(f"  Loaded: {page.url}")

        # ── Extract listings ──────────────────────────────────────────────
        print(f"Extracting up to {max_results} listings...")

        listing_cards = page.locator('div[data-cmp="inventoryListing"]')
        count = listing_cards.count()
        print(f"  Found {count} listing cards on page")

        for i in range(min(count, max_results)):
            card = listing_cards.nth(i)
            try:
                text = card.inner_text(timeout=3000)

                year_make_model = "N/A"
                img = card.locator('img[data-cmp="inventoryImage"]').first
                alt = img.get_attribute("alt", timeout=2000) or ""
                m = re.match(r"(?:Used|Certified|New)?\s*(\d{4}\s+.+?)(?:\s+w/|$)", alt)
                if m:
                    year_make_model = m.group(1).strip()
                else:
                    year_make_model = alt.replace("Used ", "").replace("Certified ", "").strip()

                price = "N/A"
                m = re.search(r"(\d{1,3}(?:,\d{3})+)\s*\n?\s*(?:See payment|See estimated)", text)
                if m:
                    price = "$" + m.group(1)
                else:
                    m = re.search(r"(\d{2,3},\d{3})", text)
                    if m:
                        price = "$" + m.group(1)

                mileage = "N/A"
                m = re.search(r"([\d,]+K?)\s*mi\b", text)
                if m:
                    mileage = m.group(1) + " mi"

                dealer = "N/A"
                m = re.search(r"Sponsored by\s+(.+?)(?:\n|$)", text)
                if m:
                    dealer = m.group(1).strip()
                else:
                    lines = [l.strip() for l in text.split("\n") if l.strip()]
                    for j, line in enumerate(lines):
                        if re.search(r"\d+\.?\d*\s*mi\.?\s*away", line):
                            for k in range(max(0, j - 3), j):
                                candidate = lines[k]
                                if (len(candidate) > 3
                                    and not re.match(r"^[\d$]", candidate)
                                    and "Request" not in candidate
                                    and "payment" not in candidate.lower()
                                    and "See " not in candidate
                                    and "Price" not in candidate
                                    and "Accident" not in candidate
                                    and "Info" not in candidate):
                                    dealer = candidate
                            break
                    if dealer == "N/A":
                        for j, line in enumerate(lines):
                            if re.search(r"\(\d{3}\)\s*\d{3}-\d{4}", line):
                                for k in range(max(0, j - 2), j):
                                    candidate = lines[k]
                                    if (len(candidate) > 3
                                        and not re.match(r"^[\d$]", candidate)
                                        and "Request" not in candidate):
                                        dealer = candidate
                                break

                if year_make_model == "N/A":
                    continue

                results.append(AutotraderListing(
                    year_make_model=year_make_model,
                    price=price,
                    mileage=mileage,
                    dealer=dealer,
                ))
            except Exception:
                continue

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nFound {len(results)} listings for '{make} {model}' near {zip_code}:\n")
        for i, car in enumerate(results, 1):
            print(f"  {i}. {car.year_make_model}")
            print(f"     Price: {car.price}  Mileage: {car.mileage}")
            print(f"     Dealer: {car.dealer}")
            print()

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return AutotraderSearchResult(
        make=make,
        model=model,
        zip_code=zip_code,
        radius_miles=radius_miles,
        listings=results,
    )


def test_search_autotrader_listings() -> None:
    request = AutotraderSearchRequest(
        make="Toyota",
        model="Camry",
        zip_code="60601",
        radius_miles=50,
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
            result = search_autotrader_listings(page, request)
            assert result.make == request.make
            assert result.model == request.model
            assert len(result.listings) <= request.max_results
            print(f"\nTotal listings found: {len(result.listings)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_autotrader_listings)
