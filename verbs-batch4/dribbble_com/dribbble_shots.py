import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class DribbbleShotsRequest:
    search_query: str = "mobile app UI"
    max_results: int = 5

@dataclass(frozen=True)
class DribbbleShot:
    title: str = ""
    designer_name: str = ""
    likes: str = ""
    views: str = ""

@dataclass(frozen=True)
class DribbbleShotsResult:
    shots: list = None  # list[DribbbleShot]

# Search for design shots on Dribbble matching a query and extract shot listings
# including title, designer name, number of likes, and number of views.
def dribbble_shots(page: Page, request: DribbbleShotsRequest) -> DribbbleShotsResult:
    search_query = request.search_query
    max_results = request.max_results
    print(f"  Search query: {search_query}")
    print(f"  Max shots to extract: {max_results}\n")

    from urllib.parse import quote_plus
    url = f"https://dribbble.com/search/shots/popular?q={quote_plus(search_query)}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to Dribbble search for '{search_query}'")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    results = []

    # Each shot is in li[id^="screenshot-"] with structure:
    #   "View <title>" (aria link), <title>, <designer>, "PRO"(optional), <likes>, <views>
    cards = page.locator('li[id^="screenshot-"]')
    count = cards.count()
    print(f"  Found {count} shot cards")

    for i in range(min(count, max_results)):
        card = cards.nth(i)
        try:
            card_text = card.inner_text(timeout=3000).strip()
            lines = [l.strip() for l in card_text.split("\n") if l.strip()]

            title = "N/A"
            designer = "N/A"
            likes = "N/A"
            views = "N/A"

            # Expected order: "View <title>", <title>, <designer>, "PRO"?, <likes>, <views>
            non_meta = [l for l in lines if l != "PRO" and not l.startswith("View ")]
            if len(non_meta) >= 1:
                title = non_meta[0]
            if len(non_meta) >= 2:
                designer = non_meta[1]
            if len(non_meta) >= 3:
                likes = non_meta[2]
            if len(non_meta) >= 4:
                views = non_meta[3]

            if title != "N/A":
                results.append(DribbbleShot(
                    title=title,
                    designer_name=designer,
                    likes=likes,
                    views=views,
                ))
        except Exception:
            continue

    print("=" * 60)

    print("=" * 60)
    print(f"Dribbble – Search Results for '{search_query}'")
    print("=" * 60)
    for idx, s in enumerate(results, 1):
        print(f"\n{idx}. {s.title}")
        print(f"   Designer: {s.designer_name}")
        print(f"   Likes: {s.likes}")
        print(f"   Views: {s.views}")

    print(f"\nFound {len(results)} shots")

    return DribbbleShotsResult(shots=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = dribbble_shots(page, DribbbleShotsRequest())
        print(f"\nReturned {len(result.shots or [])} shots")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
