"""
Playwright script (Python) — Nike Store Locator
Find Nike stores near a location with name, address, and hours.

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
class NikeStoresRequest:
    location: str
    max_results: int


@dataclass(frozen=True)
class NikeStore:
    name: str
    address: str
    hours: str


@dataclass(frozen=True)
class NikeStoresResult:
    location: str
    stores: list[NikeStore]


# Searches Nike.com store locator for stores near a location and extracts
# up to max_results stores with name, address, and hours.
def search_nike_stores(
    page: Page,
    request: NikeStoresRequest,
) -> NikeStoresResult:
    location = request.location
    max_results = request.max_results

    print(f"  Location: {location}\n")

    results: list[NikeStore] = []

    try:
        checkpoint("Navigate to https://www.nike.com/retail")
        page.goto("https://www.nike.com/retail")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        si = page.locator('#ta-Location_input')
        checkpoint(f"Fill location: {location}")
        si.click()
        page.wait_for_timeout(500)
        si.fill(location)
        page.wait_for_timeout(1000)
        checkpoint("Press Enter to search")
        page.keyboard.press("Enter")
        page.wait_for_timeout(5000)

        article_text = page.locator("article").first.inner_text(timeout=5000)
        h3s = page.locator("h3")
        count = h3s.count()

        for i in range(min(count, max_results)):
            name = h3s.nth(i).inner_text(timeout=2000).strip()
            idx = article_text.find(name)
            if idx < 0:
                continue
            block = article_text[idx + len(name):].strip()
            if i + 1 < count:
                next_name = h3s.nth(i + 1).inner_text(timeout=2000).strip()
                end_idx = block.find(next_name)
                if end_idx > 0:
                    block = block[:end_idx]
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            addr_lines = []
            hours = "N/A"
            for l in lines:
                if "Open" in l or "Close" in l or "Clos" in l:
                    hours = l
                    break
                addr_lines.append(l)
            address = ", ".join(addr_lines) if addr_lines else "N/A"
            results.append(NikeStore(name=name, address=address, hours=hours))
            print(f"  {len(results)}. {name} | {address} | {hours}")

        print(f"\nFound {len(results)} stores:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name}\n     {r.address}\n     {r.hours}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return NikeStoresResult(location=location, stores=results)


def test_search_nike_stores() -> None:
    request = NikeStoresRequest(location="Los Angeles, CA", max_results=3)
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
            result = search_nike_stores(page, request)
            assert result.location == request.location
            assert len(result.stores) <= request.max_results
            print(f"\nTotal stores found: {len(result.stores)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_nike_stores)
