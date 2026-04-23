"""
Playwright script (Python) — Walmart Store Finder
Find Walmart stores near a location with name, address, hours, and phone.

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
class WalmartStoresRequest:
    location: str
    max_results: int


@dataclass(frozen=True)
class WalmartStore:
    name: str
    address: str
    hours: str
    phone: str


@dataclass(frozen=True)
class WalmartStoresResult:
    location: str
    stores: list[WalmartStore]


# Searches the Walmart store finder for stores near a location and extracts
# up to max_results stores with name, address, hours, and phone/ID.
def search_walmart_stores(
    page: Page,
    request: WalmartStoresRequest,
) -> WalmartStoresResult:
    location = request.location
    max_results = request.max_results

    print(f"  Location: {location}\n")

    results: list[WalmartStore] = []

    try:
        loc = urllib.parse.quote(location)
        url = f"https://www.walmart.com/store-finder?location={loc}"
        checkpoint(f"Navigate to {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)

        body = page.locator("body").inner_text(timeout=5000)
        if "0 stores near" in body:
            si = page.locator("#zip-code-or-city-state")
            checkpoint(f"Fill location: {location}")
            si.click()
            page.wait_for_timeout(300)
            si.fill(location)
            page.wait_for_timeout(500)
            checkpoint("Click Find store button")
            page.locator('button:has-text("Find store")').first.evaluate("el => el.click()")
            page.wait_for_timeout(5000)

        body = page.locator("body").inner_text(timeout=5000)
        lines = [l.strip() for l in body.split("\n") if l.strip()]
        i = 0
        while i < len(lines) and len(results) < max_results:
            if i + 2 < len(lines) and re.match(r'Walmart\s+(Supercenter|Neighborhood)', lines[i + 1]):
                name = lines[i]
                store_id = lines[i + 1]
                address = lines[i + 2] if i + 2 < len(lines) else "N/A"
                hours = "N/A"
                if i + 3 < len(lines) and ("Open" in lines[i + 3] or "Close" in lines[i + 3]):
                    hours = lines[i + 3].replace("·", " ").strip()
                results.append(WalmartStore(name=name, address=address, hours=hours, phone=store_id))
                print(f"  {len(results)}. {name} | {address} | {hours}")
                i += 4
            else:
                i += 1

        print(f"\nFound {len(results)} stores:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.address}\n     Hours: {r.hours}\n     Phone: {r.phone}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return WalmartStoresResult(location=location, stores=results)


def test_search_walmart_stores() -> None:
    request = WalmartStoresRequest(location="78701", max_results=3)
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
            result = search_walmart_stores(page, request)
            assert result.location == request.location
            assert len(result.stores) <= request.max_results
            print(f"\nTotal stores found: {len(result.stores)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_walmart_stores)
