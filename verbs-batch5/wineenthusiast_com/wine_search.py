"""
Auto-generated Playwright script (Python)
Wine Enthusiast – Wine Reviews
Query: "Pinot Noir Oregon"

Generated on: 2026-04-18T02:53:01.924Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
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
class WineRequest:
    query: str = "Pinot Noir Oregon"
    max_wines: int = 5


@dataclass
class WineReview:
    wine_name: str = ""
    winery: str = ""
    vintage: str = ""
    rating: str = ""
    price: str = ""
    tasting_notes: str = ""


@dataclass
class WineResult:
    wines: list = field(default_factory=list)


def wine_search(page: Page, request: WineRequest) -> WineResult:
    """Search Wine Enthusiast for wine reviews."""
    print(f"  Query: {request.query}\n")

    # ── Search ────────────────────────────────────────────────────────
    search_url = f"https://www.winemag.com/?s={quote_plus(request.query)}&search_type=ratings"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to Wine Enthusiast search")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    # ── Extract wines ─────────────────────────────────────────────────
    raw_wines = page.evaluate(r"""(maxWines) => {
        const text = document.body.innerText;
        // Pattern: WineName YYYY Variety(Region) / NN Points | Price / Tasting notes / See Full Review
        const pattern = /(.+?\s(\d{4})\s.+?)\n(\d+)\sPoints\s\|\s(\$[\d.]+).*?\n(.+?)\nSee Full Review/g;
        const results = [];
        let m;
        while ((m = pattern.exec(text)) && results.length < maxWines) {
            const fullName = m[1].trim();
            const vintage = m[2];
            // Winery = text before vintage year
            const winery = fullName.substring(0, fullName.indexOf(vintage)).trim();
            results.push({
                wine_name: fullName,
                winery: winery,
                vintage: vintage,
                rating: m[3] + ' Points',
                price: m[4],
                tasting_notes: m[5].trim(),
            });
        }
        return results;
    }""", request.max_wines)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Wine Enthusiast: {request.query}")
    print("=" * 60)
    for idx, w in enumerate(raw_wines, 1):
        print(f"\n  {idx}. {w['wine_name']}")
        print(f"     Winery: {w['winery']}")
        print(f"     Vintage: {w['vintage']}")
        print(f"     Rating: {w['rating']}")
        print(f"     Price: {w['price']}")
        print(f"     Notes: {w['tasting_notes'][:100]}...")

    wines = [WineReview(**w) for w in raw_wines]
    return WineResult(wines=wines)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("wineenthusiast_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = wine_search(page, WineRequest())
            print(f"\nReturned {len(result.wines)} wines")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
