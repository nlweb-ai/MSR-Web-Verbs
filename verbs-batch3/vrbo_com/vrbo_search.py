"""
VRBO – Vacation Rental Search
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
class VrboSearchRequest:
    destination: str
    guests: int
    checkin: str
    checkout: str
    max_results: int = 5


@dataclass(frozen=True)
class VrboProperty:
    name: str
    nightly_price: str
    bedrooms: str
    bathrooms: str
    rating: str


@dataclass(frozen=True)
class VrboSearchResult:
    properties: list[VrboProperty]


# Search VRBO for vacation rental properties at a given destination, date range,
# and guest count. Returns up to max_results properties with name, nightly price,
# bedrooms, bathrooms, and rating.
def vrbo_search(page: Page, request: VrboSearchRequest) -> VrboSearchResult:
    destination = request.destination
    checkin_str = request.checkin
    checkout_str = request.checkout
    guests = request.guests
    max_results = request.max_results

    print(f"  Destination: {destination}")
    print(f"  Guests: {guests}")
    print(f"  Check-in: {checkin_str}  Check-out: {checkout_str}\n")

    # ── Navigate directly to search results ──────────────────────────
    dest_encoded = destination.replace(" ", "+")
    search_url = (
        f"https://www.vrbo.com/search"
        f"?destination={dest_encoded}"
        f"&startDate={checkin_str}&endDate={checkout_str}"
        f"&adults={guests}"
    )
    print(f"Loading {search_url}...")
    checkpoint("Navigate to page")
    page.goto(search_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    # ── Dismiss cookie consent ────────────────────────────────────────
    for selector in [
        "button#onetrust-accept-btn-handler",
        "button:has-text('Accept All')",
        "button:has-text('Accept')",
    ]:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=1500):
                checkpoint("Click element")
                btn.evaluate("el => el.click()")
                page.wait_for_timeout(500)
                break
        except Exception:
            pass

    # ── Wait for property cards ───────────────────────────────────────
    print("Waiting for property listings...")
    try:
        page.locator('[data-stid="lodging-card-responsive"]').first.wait_for(
            state="visible", timeout=15000
        )
    except Exception:
        pass
    page.wait_for_timeout(2000)
    print(f"  Loaded: {page.url}")

    # ── Extract properties ────────────────────────────────────────────
    print(f"Extracting up to {max_results} properties...")

    cards = page.locator('[data-stid="lodging-card-responsive"]')
    count = cards.count()
    print(f"  Found {count} property cards on page")

    results: list[VrboProperty] = []

    for i in range(min(count, max_results)):
        card = cards.nth(i)
        try:
            text = card.inner_text(timeout=3000)
            lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

            # ── Property name ─────────────────────────────────────────
            name = "N/A"
            details_idx = -1
            for j, ln in enumerate(lines):
                if re.search(r"\d+\s*bedroom", ln, re.I):
                    details_idx = j
                    break
            if details_idx > 0:
                name = lines[details_idx - 1]
                name = re.sub(r"^Opens\s+", "", name)
                name = re.sub(r"\s+in new tab$", "", name)

            # ── Bedrooms / Bathrooms ──────────────────────────────────
            bedrooms = "N/A"
            bathrooms = "N/A"
            if details_idx >= 0:
                detail_line = lines[details_idx]
                m_bed = re.search(r"(\d+)\s*bedroom", detail_line, re.I)
                if m_bed:
                    bedrooms = m_bed.group(1)
                m_bath = re.search(r"(\d+)\s*bathroom", detail_line, re.I)
                if m_bath:
                    bathrooms = m_bath.group(1)

            # ── Rating ────────────────────────────────────────────────
            rating = "N/A"
            for ln in lines:
                m = re.match(r"^(\d+\.?\d*)\s+out of\s+10$", ln)
                if m:
                    rating = m.group(1)
                    break

            # ── Nightly price ─────────────────────────────────────────
            nightly_price = "N/A"
            for ln in lines:
                if "current price" in ln.lower():
                    m = re.search(r"\$[\d,]+", ln)
                    if m:
                        nightly_price = m.group(0)
                    break
            if nightly_price == "N/A":
                for ln in lines:
                    m = re.search(r"\$([\d,]+)\s+for\s+(\d+)\s+night", ln, re.I)
                    if m:
                        total = int(m.group(1).replace(",", ""))
                        n = int(m.group(2))
                        nightly_price = f"${total // n:,}"
                        break

            if name == "N/A":
                continue

            results.append(VrboProperty(
                name=name,
                nightly_price=nightly_price,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                rating=rating,
            ))
        except Exception:
            continue

    # ── Print results ─────────────────────────────────────────────────
    print(f'\nFound {len(results)} properties in "{destination}":\n')
    for i, prop in enumerate(results, 1):
        print(f"  {i}. {prop.name}")
        print(f"     Price/night: {prop.nightly_price}  Bedrooms: {prop.bedrooms}  Bathrooms: {prop.bathrooms}  Rating: {prop.rating}")
        print()

    return VrboSearchResult(properties=results)


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    from datetime import date, timedelta
    from dateutil.relativedelta import relativedelta

    checkin = date.today() + relativedelta(months=2)
    checkout = checkin + timedelta(days=6)

    with sync_playwright() as p:
        chrome_user_data = os.path.join(
            os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default"
        )
        context = p.chromium.launch_persistent_context(
            chrome_user_data,
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        request = VrboSearchRequest(
            destination="Lake Tahoe",
            guests=4,
            checkin=checkin.strftime("%Y-%m-%d"),
            checkout=checkout.strftime("%Y-%m-%d"),
            max_results=5,
        )
        result = vrbo_search(page, request)
        print(f"\nTotal properties found: {len(result.properties)}")

        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
