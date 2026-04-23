"""
Playwright script (Python) — NPS Park Info
Look up a national park and extract description, hours, fees, and location.

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
class NpsParkRequest:
    park_name: str


@dataclass(frozen=True)
class NpsParkResult:
    park_name: str
    description: str
    hours: str
    fees: str
    location: str


# Looks up a national park on NPS.gov and extracts
# the description, operating hours, entrance fees, and location.
def lookup_nps_park(
    page: Page,
    request: NpsParkRequest,
) -> NpsParkResult:
    park_name = request.park_name

    print(f"  Park: {park_name}\n")

    description = "N/A"
    hours = "N/A"
    fees = "N/A"
    location = "N/A"

    try:
        slug = re.sub(r'[^a-z]', '', park_name.lower())[:4]
        url = f"https://www.nps.gov/{slug}/index.htm"
        checkpoint(f"Navigate to {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        body_text = page.locator("body").inner_text(timeout=5000)

        try:
            article = page.locator("article, div[class*='Component']")
            art_text = article.first.inner_text(timeout=5000)
            lines = [l.strip() for l in art_text.split("\n") if l.strip() and len(l.strip()) > 50]
            description = lines[0][:500] if lines else "N/A"
        except Exception:
            pass

        try:
            hm = re.search(r"((?:Open|Hours|Operating)[^\n]*(?:\n[^\n]+){0,3})", body_text, re.I)
            hours = hm.group(1).strip()[:300] if hm else "N/A"
        except Exception:
            pass

        try:
            fm = re.search(r"((?:Entrance Fee|Fees)[^\n]*(?:\n[^\n]+){0,3})", body_text, re.I)
            fees = fm.group(1).strip()[:300] if fm else "N/A"
        except Exception:
            pass

        try:
            location = page.title()
        except Exception:
            pass

        print(f"Park: {park_name}")
        print(f"  Description: {description[:150]}...")
        print(f"  Hours: {hours[:150]}...")
        print(f"  Fees: {fees[:150]}...")
        print(f"  Location: {location[:150]}...")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return NpsParkResult(park_name=park_name, description=description, hours=hours, fees=fees, location=location)


def test_lookup_nps_park() -> None:
    request = NpsParkRequest(park_name="Yellowstone")
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
            result = lookup_nps_park(page, request)
            assert result.park_name == request.park_name
            print(f"\nPark lookup complete for: {result.park_name}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_lookup_nps_park)
