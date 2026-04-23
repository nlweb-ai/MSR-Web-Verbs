"""
Playwright verb — Starbucks Store Locator
Find stores near a given location.
Extract store name, address, hours, distance, and available features.

URL: https://www.starbucks.com/store-locator
"""

import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


HOURS_RE = re.compile(
    r"^([\d.]+)\s+miles?\s+away\s+·\s+(.+)$"
)


@dataclass(frozen=True)
class StarbucksStoreLocatorRequest:
    location: str = "Manhattan, NY"
    max_results: int = 5


@dataclass(frozen=True)
class StarbucksStoreInfo:
    name: str = ""
    address: str = ""
    hours: str = ""
    distance: str = ""
    features: str = ""


@dataclass(frozen=True)
class StarbucksStoreLocatorResult:
    stores: list = ()  # list[StarbucksStoreInfo]


# Use the Starbucks store locator to find stores near a location.
# Type the location into the search field and press Enter.
# Extract up to max_results stores with name, address, hours, distance, and features.
def starbucks_store_locator(page: Page, request: StarbucksStoreLocatorRequest) -> StarbucksStoreLocatorResult:
    location = request.location
    max_results = request.max_results
    print(f"  Location: {location}")
    print(f"  Max results: {max_results}\n")

    results = []

    checkpoint("Navigating to Starbucks store locator")
    page.goto("https://www.starbucks.com/store-locator", timeout=30000)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)

    # Accept cookies if present
    try:
        agree = page.locator('button:has-text("Agree")').first
        if agree.is_visible(timeout=2000):
            checkpoint("Accepting cookies")
            agree.click()
            page.wait_for_timeout(1000)
    except Exception:
        pass

    # Type location into search
    checkpoint("Typing location into search field")
    search = page.locator('input[data-e2e="searchTermInput"]').first
    search.click()
    page.wait_for_timeout(300)
    search.fill(location)
    page.wait_for_timeout(1500)

    checkpoint("Pressing Enter to search")
    page.keyboard.press("Enter")
    page.wait_for_timeout(8000)
    print(f"  Searched: {page.url}")

    body = page.locator("body").inner_text(timeout=10000)
    lines = [l.strip() for l in body.split("\n") if l.strip()]

    # Find "Stores near <location>" header
    start_idx = 0
    for i, l in enumerate(lines):
        if "Stores near" in l or "stores near" in l:
            start_idx = i + 1
            print(f"  Found results header at line {i}: {l}")
            break

    # Parse store blocks: name → address → distance/hours → order-type
    i = start_idx
    while i < len(lines) and len(results) < max_results:
        line = lines[i]
        m = HOURS_RE.match(line)
        if m:
            distance = m.group(1) + " miles"
            hours = m.group(2).strip()
            name = lines[i - 2] if i >= 2 else "N/A"
            address = lines[i - 1] if i >= 1 else "N/A"

            features = []
            j = i + 1
            while j < len(lines):
                cand = lines[j]
                if cand in ("In store", "Order Here", "Pickup", "Delivery"):
                    features.append(cand)
                    j += 1
                else:
                    break

            results.append(StarbucksStoreInfo(
                name=name,
                address=address,
                hours=hours,
                distance=distance,
                features=", ".join(features) if features else "N/A",
            ))
            i = j
            continue
        i += 1

    print(f'\nFound {len(results)} stores near "{location}":\n')
    for idx, s in enumerate(results, 1):
        print(f"  {idx}. {s.name}")
        print(f"     Address: {s.address}")
        print(f"     Hours: {s.hours}")
        print(f"     Distance: {s.distance}")
        print(f"     Features: {s.features}")
        print()

    return StarbucksStoreLocatorResult(stores=results)


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_user_data = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            chrome_user_data,
            headless=False,
            channel="chrome",
        )
        page = context.pages[0] if context.pages else context.new_page()
        request = StarbucksStoreLocatorRequest(location="Manhattan, NY", max_results=5)
        result = starbucks_store_locator(page, request)
        print(f"\nTotal stores found: {len(result.stores)}")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
