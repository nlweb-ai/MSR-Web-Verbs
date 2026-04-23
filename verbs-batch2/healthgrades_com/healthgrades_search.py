"""
Playwright script (Python) — Healthgrades Doctor Search
Search for doctors by specialty near a location.

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
class HealthgradesSearchRequest:
    specialty: str
    location: str
    max_results: int


@dataclass(frozen=True)
class HealthgradesDoctor:
    name: str
    rating: str
    specialty: str


@dataclass(frozen=True)
class HealthgradesSearchResult:
    specialty: str
    location: str
    doctors: list[HealthgradesDoctor]


# Searches Healthgrades for doctors by specialty near a location and extracts
# up to max_results doctors with name, rating, and specialty.
def search_healthgrades(
    page: Page,
    request: HealthgradesSearchRequest,
) -> HealthgradesSearchResult:
    specialty = request.specialty
    location = request.location
    max_results = request.max_results

    print(f"  Specialty: {specialty}")
    print(f"  Location: {location}")
    print(f"  Max results: {max_results}\n")

    results: list[HealthgradesDoctor] = []

    try:
        search_url = f"https://www.healthgrades.com/usearch?what={specialty.replace(' ', '+')}&where={location.replace(' ', '+').replace(',', '%2C')}"
        print("Loading Healthgrades search results...")
        checkpoint(f"Navigate to {search_url}")
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(4000)

        for selector in ["button#onetrust-accept-btn-handler", "button:has-text('Accept')", "button:has-text('Close')"]:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {selector}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        print(f'STEP 1: Extract up to {max_results} doctors for "{specialty}" near "{location}"...')
        h3s = page.locator("h3")
        count = h3s.count()
        print(f"  Found {count} doctor headings")

        for i in range(count):
            if len(results) >= max_results:
                break
            h3 = h3s.nth(i)
            try:
                name = h3.inner_text(timeout=2000).strip()
                if not name or not name.startswith("Dr."):
                    continue
                card_text = h3.evaluate(
                    "el => { let p = el.parentElement; while(p && !p.className.includes('card')) p = p.parentElement; return p ? p.innerText : el.parentElement.parentElement.innerText; }"
                )
                spec_match = re.search(r"Specialty:\s*(.+?)(?:\n|$)", card_text)
                spec = spec_match.group(1).strip() if spec_match else "N/A"
                rating_match = re.search(r"([\d.]+)\s+(?:out of|/)\s*5", card_text)
                rating = rating_match.group(1) if rating_match else "N/A"

                results.append(HealthgradesDoctor(name=name, rating=rating, specialty=spec))
                print(f"  {len(results)}. {name} | Rating: {rating} | {spec}")
            except Exception:
                continue

        print(f"\nFound {len(results)} doctors for '{specialty}' near '{location}':")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name}")
            print(f"     Rating: {r.rating}  Specialty: {r.specialty}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return HealthgradesSearchResult(specialty=specialty, location=location, doctors=results)


def test_search_healthgrades() -> None:
    request = HealthgradesSearchRequest(specialty="dentist", location="Chicago, IL", max_results=5)
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
            result = search_healthgrades(page, request)
            assert result.specialty == request.specialty
            assert result.location == request.location
            assert len(result.doctors) <= request.max_results
            print(f"\nTotal doctors found: {len(result.doctors)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_healthgrades)
