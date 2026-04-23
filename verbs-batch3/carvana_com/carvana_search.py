"""
Playwright script (Python) — Carvana Car Search
Query: Honda Civic   Max results: 5

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
class CarvanaSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class CarvanaListing:
    year_model: str
    trim: str
    mileage: str
    price: str
    monthly_payment: str


@dataclass(frozen=True)
class CarvanaSearchResult:
    query: str
    listings: list[CarvanaListing]


# Searches Carvana for cars matching the given query and returns up to max_results
# listings with year/model, trim, mileage, price, and monthly payment.
def search_carvana_cars(
    page: Page,
    request: CarvanaSearchRequest,
) -> CarvanaSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}  Max results: {max_results}\n")

    results: list[CarvanaListing] = []

    try:
        # ── Navigate ──────────────────────────────────────────────────
        print("Loading Carvana search results...")
        slug = query.lower().replace(" ", "-")
        search_url = f"https://www.carvana.com/cars/{slug}"
        checkpoint(f"Navigate to {search_url}")
        page.goto(search_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        print(f"  Loaded: {page.url}")

        # ── Extract cars ──────────────────────────────────────────────
        print(f"Extracting up to {max_results} cars...")

        body_text = page.evaluate("document.body.innerText") or ""
        lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        i = 0
        while i < len(lines) and len(results) < max_results:
            m = re.match(r"^(\d{4})\s+(.+)$", lines[i])
            if m and int(m.group(1)) >= 2000 and int(m.group(1)) <= 2030:
                year_model = lines[i]
                trim = "N/A"
                mileage = "N/A"
                price = "N/A"
                monthly = "N/A"

                for k in range(i + 1, min(i + 8, len(lines))):
                    line = lines[k]
                    if re.match(r"^\d+k miles$", line):
                        mileage = line
                    elif re.match(r"^\$[\d,]+$", line) and price == "N/A":
                        price = line
                    elif re.match(r"^\$[\d,]+/mo$", line):
                        monthly = line
                    elif trim == "N/A" and k == i + 1 and not line.startswith("$") and "miles" not in line:
                        trim = line

                if price != "N/A":
                    results.append(CarvanaListing(
                        year_model=year_model,
                        trim=trim,
                        mileage=mileage,
                        price=price,
                        monthly_payment=monthly,
                    ))

            i += 1

        # ── Print results ─────────────────────────────────────────────
        print(f"\nFound {len(results)} cars:\n")
        for i, car in enumerate(results, 1):
            print(f"  {i}. {car.year_model} — {car.trim}")
            print(f"     Price: {car.price}  Mileage: {car.mileage}  Monthly: {car.monthly_payment}")
            print()

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return CarvanaSearchResult(
        query=query,
        listings=results,
    )


def test_search_carvana_cars() -> None:
    request = CarvanaSearchRequest(
        query="Honda Civic",
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
            result = search_carvana_cars(page, request)
            assert result.query == request.query
            assert len(result.listings) <= request.max_results
            print(f"\nTotal cars found: {len(result.listings)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_carvana_cars)
