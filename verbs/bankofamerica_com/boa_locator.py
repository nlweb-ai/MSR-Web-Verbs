"""
Auto-generated Playwright script (Python)
Bank of America – Branch & ATM Locator
Location: Redmond, WA 98052
Max results: 5

Generated on: 2026-02-27T23:39:05.640Z
Recorded 8 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os
import traceback
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

from dataclasses import dataclass

@dataclass(frozen=True)
class BoaLocatorRequest:
    location: str
    max_results: int

@dataclass(frozen=True)
class BoaLocation:
    name: str
    address: str
    distance: str

@dataclass(frozen=True)
class BoaLocatorResult:
    location: str
    locations: list[BoaLocation]


# Locates Bank of America branches and ATMs near a location, returning up to max_results results.
def locate_boa_branches(
    page: Page,
    request: BoaLocatorRequest,
) -> BoaLocatorResult:
    location = request.location
    max_results = request.max_results
    raw_results = []
    print("=" * 59)
    print("  Bank of America – Branch & ATM Locator")
    print("=" * 59)
    print(f"  Location: {location}")
    print(f"  Max raw_results: {max_results}\n")

    raw_results = []

    try:
        # ── Navigate ──────────────────────────────────────────────────────
        print("Loading Bank of America Locator...")
        checkpoint("Navigate to Bank of America Locator")
        page.goto("https://www.bankofamerica.com/locator/")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)
        print(f"  Loaded: {page.url}")

        # ── Dismiss popups / cookie banners ───────────────────────────────
        for selector in [
            "button#onetrust-accept-btn-handler",
            "button:has-text('Accept')",
            "button:has-text('Accept All')",
            "button:has-text('Got it')",
            "button:has-text('Close')",
            "[aria-label='Close']",
        ]:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {selector}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        # ── STEP 1: Enter location in search box ─────────────────────────
        print(f"STEP 1: Search for '{location}'...")
        # Concrete selectors from recorded JS run
        search_input = page.locator(
            "#q, "
            "input[name='locator-search-value'], "
            "input[aria-label='Enter address, ZIP code or landmark'], "
            "#map-search-form input[type='text']"
        ).first
        try:
            search_input.wait_for(state="visible", timeout=10000)
        except Exception:
            # Fallback: find any visible text input inside the search form
            search_input = page.locator("form input[type='text']:visible").first
            search_input.wait_for(state="visible", timeout=5000)
        checkpoint(f"Click and type location: {location}")
        search_input.evaluate("el => el.click()")
        page.keyboard.press("Control+a")
        page.keyboard.press("Backspace")
        search_input.type(location, delay=50)
        print(f"  Typed '{location}'")
        page.wait_for_timeout(1000)

        # ── STEP 2: Submit search ─────────────────────────────────────────
        print("STEP 2: Submit search...")
        # Try clicking a search/submit button (concrete selectors from recorded JS run)
        submitted = False
        for sel in [
            "#search-button",
            "button[aria-label='Click to submit search form']",
            "#map-search-form button[type='submit']",
            "button[type='submit']",
            "button:has-text('Search')",
        ]:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=2000):
                    checkpoint("Click Search button")
                    btn.evaluate("el => el.click()")
                    submitted = True
                    print("  Clicked Search button")
                    break
            except Exception:
                pass
        if not submitted:
            checkpoint("Press Enter to submit")
            page.keyboard.press("Enter")
            print("  Pressed Enter")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)
        print(f"  URL: {page.url}")

        # ── STEP 3: Extract raw_results ───────────────────────────────────────
        print(f"STEP 3: Extract up to {max_results} raw_results...")

        # Wait for result cards to load
        page.wait_for_timeout(3000)

        # Concrete selectors discovered from the live page DOM:
        #   Card:     li.map-list-item-wrap.is-visible
        #   Name:     button.location-name  (short name like "Redmond")
        #   Type:     div.location-type     (e.g. "Financial Center & ATM")
        #   Distance: div.distance:not(.feet) span  (e.g. "0.3 mi")
        #   Address:  first line of div.map-list-item-inner innerText
        cards = page.locator("li.map-list-item-wrap.is-visible")
        count = cards.count()
        print(f"  Found {count} result cards")

        seen_names = set()
        for i in range(count):
            if len(raw_results) >= max_results:
                break
            card = cards.nth(i)
            try:
                # Name + type
                name = "N/A"
                loc_type = ""
                try:
                    name = card.locator("button.location-name").first.inner_text(timeout=2000).strip()
                except Exception:
                    pass
                try:
                    loc_type = card.locator("div.location-type").first.inner_text(timeout=2000).strip()
                except Exception:
                    pass
                if name != "N/A" and loc_type:
                    name = f"{name} {loc_type}"

                # Address (first line of .map-list-item-inner)
                address = "N/A"
                try:
                    inner_text = card.locator("div.map-list-item-inner").first.inner_text(timeout=2000).strip()
                    if inner_text:
                        address = inner_text.split("\n")[0].strip()
                except Exception:
                    pass

                # Distance
                distance = "N/A"
                try:
                    dist_el = card.locator("div.distance:not(.feet) span").first
                    distance = dist_el.inner_text(timeout=2000).strip()
                except Exception:
                    card_text = card.inner_text(timeout=2000)
                    dist_match = re.search(r"([\d.]+)\s*mi", card_text, re.IGNORECASE)
                    if dist_match:
                        distance = dist_match.group(0)

                if name == "N/A":
                    continue
                name_key = name.lower().strip()
                if name_key in seen_names:
                    continue
                seen_names.add(name_key)

                raw_results.append({
                    "name": name,
                    "address": address,
                    "distance": distance,
                })
            except Exception:
                continue

        # Fallback: regex-based extraction from full page text
        if not raw_results:
            print("  Card extraction failed, trying text fallback...")
            body_text = page.evaluate("document.body.innerText") or ""
            lines = [l.strip() for l in body_text.split("\n") if l.strip()]
            for i, line in enumerate(lines):
                if len(raw_results) >= max_results:
                    break
                dm = re.search(r"([\d.]+)\s*mi", line, re.IGNORECASE)
                if dm and len(line) < 20:
                    name = "N/A"
                    address = "N/A"
                    # Walk backwards to find name and address
                    for j in range(i - 1, max(0, i - 6), -1):
                        candidate = lines[j]
                        if re.match(r"\d+\s+\w", candidate) and address == "N/A":
                            address = candidate
                        elif len(candidate) > 3 and name == "N/A" and candidate not in ("Make my favorite",):
                            name = candidate
                    raw_results.append({
                        "name": name,
                        "address": address,
                        "distance": dm.group(0),
                    })

        # ── Print raw_results ─────────────────────────────────────────────────
        print(f"\nFound {len(raw_results)} locations near '{location}':\n")
        for i, loc in enumerate(raw_results, 1):
            print(f"  {i}. {loc['name']}")
            print(f"     Address:  {loc['address']}")
            print(f"     Distance: {loc['distance']}")

    except Exception as e:
        print(f"\nError: {e}")
        traceback.print_exc()

    return BoaLocatorResult(
        location=location,
        locations=[BoaLocation(name=r["name"], address=r["address"], distance=r["distance"]) for r in raw_results],
    )
def test_locate_boa_branches() -> None:
    request = BoaLocatorRequest(location="Redmond, WA 98052", max_results=5)
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
            result = locate_boa_branches(page, request)
            assert result.location == request.location
            assert len(result.locations) <= request.max_results
            print(f"\nTotal locations found: {len(result.locations)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_locate_boa_branches)
