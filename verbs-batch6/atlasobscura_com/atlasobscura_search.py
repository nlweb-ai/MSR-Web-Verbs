"""
Auto-generated Playwright script (Python)
Atlas Obscura – Place Search
Query: "underground caves"

Generated on: 2026-04-18T04:51:27.072Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class PlaceRequest:
    query: str = "underground caves"
    max_places: int = 5


@dataclass
class Place:
    name: str = ""
    location: str = ""
    description: str = ""
    url: str = ""


@dataclass
class PlaceResult:
    places: list = field(default_factory=list)


def atlasobscura_search(page: Page, request: PlaceRequest) -> PlaceResult:
    """Search Atlas Obscura for unusual places."""
    print(f"  Query: {request.query}\n")

    url = f"https://www.atlasobscura.com/search?q={quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Atlas Obscura search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract place listings")
    places_data = page.evaluate(r"""(maxPlaces) => {
        const results = [];
        const cards = document.querySelectorAll(
            '.search-result, .content-card, article, [class*="Card"], a[href*="/places/"]'
        );
        const seen = new Set();
        for (const card of cards) {
            if (results.length >= maxPlaces) break;
            const linkEl = card.tagName === 'A' ? card : card.querySelector('a[href*="/places/"]');
            const url = linkEl ? linkEl.href : '';

            const titleEl = card.querySelector('h2, h3, h4, .title, [class*="title"]');
            const name = titleEl ? titleEl.innerText.trim() : '';
            if (!name || name.length < 3 || seen.has(name)) continue;
            seen.add(name);

            const locEl = card.querySelector('[class*="location"], .subtitle, .place-card-location');
            const location = locEl ? locEl.innerText.trim() : '';

            const descEl = card.querySelector('p, .description, [class*="desc"]');
            const description = descEl ? descEl.innerText.trim().slice(0, 200) : '';

            results.push({ name, location, description, url });
        }
        return results;
    }""", request.max_places)

    result = PlaceResult(places=[Place(**p) for p in places_data])

    print("\n" + "=" * 60)
    print(f"Atlas Obscura: {request.query}")
    print("=" * 60)
    for p in result.places:
        print(f"  {p.name}")
        print(f"    Location:    {p.location}")
        print(f"    Description: {p.description[:80]}...")
        print(f"    URL: {p.url}")
    print(f"\n  Total: {len(result.places)} places")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("atlasobscura_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = atlasobscura_search(page, PlaceRequest())
            print(f"\nReturned {len(result.places)} places")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
