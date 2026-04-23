"""
Playwright script (Python) — Trader Joe's Store Locator
Find Trader Joe's stores near a location with name, address, and hours.

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
class TraderJoesStoresRequest:
    location: str
    max_results: int


@dataclass(frozen=True)
class TraderJoesStore:
    name: str
    address: str
    hours: str


@dataclass(frozen=True)
class TraderJoesStoresResult:
    location: str
    stores: list[TraderJoesStore]


# Searches the Trader Joe's store locator for stores near a location and extracts
# up to max_results stores with name, address, and hours.
def search_traderjoes_stores(
    page: Page,
    request: TraderJoesStoresRequest,
) -> TraderJoesStoresResult:
    location = request.location
    max_results = request.max_results

    print(f"  Location: {location}\n")

    results: list[TraderJoesStore] = []

    try:
        checkpoint("Navigate to https://www.traderjoes.com/stores")
        page.goto("https://www.traderjoes.com/stores")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)

        frame = page.frame_locator('iframe[src*="where2getit"]')
        si = frame.locator('#inputaddress')
        checkpoint(f"Fill location: {location}")
        si.fill(location)
        page.wait_for_timeout(500)
        checkpoint("Press Enter to search")
        si.press("Enter")
        page.wait_for_timeout(4000)

        body = frame.locator("body").inner_text(timeout=5000)
        store_blocks = re.split(r'\n(?=[A-Z][^\n]*\(\d+\)\s*\n)', body)

        for block in store_blocks:
            if len(results) >= max_results:
                break
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not lines:
                continue
            m = re.match(r'^(.+?)\s*\(\d+\)\s*$', lines[0])
            if not m:
                continue
            name = m.group(1)
            address = "N/A"
            hours = "N/A"
            for j, line in enumerate(lines):
                if "GET DIRECTIONS" in line:
                    addr_lines = [l for l in lines[1:j] if l and l != "\xa0"]
                    address = ", ".join(addr_lines)
                    break
            for line in lines:
                if re.search(r'\d+\s*[AP]M\s*-\s*\d+\s*[AP]M', line):
                    hours = re.sub(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s*:\s*', '', line).strip()
                    break
            results.append(TraderJoesStore(name=name, address=address, hours=hours))
            print(f"  {len(results)}. {name} | {address} | {hours}")

        print(f"\nFound {len(results)} stores:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name}\n     {r.address}\n     {r.hours}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return TraderJoesStoresResult(location=location, stores=results)


def test_search_traderjoes_stores() -> None:
    request = TraderJoesStoresRequest(location="Portland, OR", max_results=3)
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
            result = search_traderjoes_stores(page, request)
            assert result.location == request.location
            assert len(result.stores) <= request.max_results
            print(f"\nTotal stores found: {len(result.stores)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_traderjoes_stores)
