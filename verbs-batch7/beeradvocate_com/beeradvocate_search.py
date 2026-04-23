"""
Auto-generated Playwright script (Python)
BeerAdvocate – Beer Style Search
Style: "stout" (ID: 157)

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BeerSearchRequest:
    beer_style: str = "stout"
    style_id: int = 157
    max_beers: int = 5


@dataclass
class Beer:
    beer_name: str = ""
    brewery: str = ""
    style: str = ""
    abv: str = ""
    rating_score: str = ""
    num_reviews: str = ""


@dataclass
class BeerSearchResult:
    beers: List[Beer] = field(default_factory=list)


def beeradvocate_search(page: Page, request: BeerSearchRequest) -> BeerSearchResult:
    """Search BeerAdvocate for top beers of a given style."""
    print(f"  Style: {request.beer_style}\n")

    # ── Navigate to style page ────────────────────────────────────────
    url = f"https://www.beeradvocate.com/beer/styles/{request.style_id}/"
    print(f"Loading {url}...")
    checkpoint("Navigate to BeerAdvocate style page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = BeerSearchResult()

    # ── Extract style name from page title ────────────────────────────
    style_name = page.title().replace(" | BeerAdvocate", "").strip()

    # ── Extract beer rows via page.evaluate ───────────────────────────
    checkpoint("Extract beer list")
    beers_data = page.evaluate("""(maxBeers) => {
        const results = [];
        // Beer links in #ba-content point to /beer/profile/
        const links = document.querySelectorAll('#ba-content a[href*="/beer/profile/"]');
        let i = 0;
        while (i < links.length && results.length < maxBeers) {
            const nameLink = links[i];
            const name = nameLink.innerText.trim();
            if (!name || name.length < 2) { i++; continue; }
            // Next link is the brewery
            const breweryLink = links[i + 1];
            const brewery = breweryLink ? breweryLink.innerText.trim() : '';
            // Get the parent row text to parse ABV, ratings, avg
            const row = nameLink.closest('tr') || nameLink.parentElement;
            const rowText = row ? row.innerText : '';
            const parts = rowText.split('\\t').map(s => s.trim());
            let abv = '', ratings = '', avg = '';
            for (const p of parts) {
                if (/^\\d+\\.\\d+$/.test(p) && !abv) abv = p + '%';
                else if (/^[\\d,]+$/.test(p.replace(/,/g, '')) && !ratings) ratings = p;
                else if (/^\\d+\\.\\d+$/.test(p) && abv) avg = p;
            }
            results.push({name, brewery, abv, ratings, avg});
            i += 2;
        }
        return results;
    }""", request.max_beers)

    for bd in beers_data:
        beer = Beer()
        beer.beer_name = bd.get("name", "")
        beer.brewery = bd.get("brewery", "")
        beer.style = style_name
        beer.abv = bd.get("abv", "")
        beer.rating_score = bd.get("avg", "")
        beer.num_reviews = bd.get("ratings", "")
        result.beers.append(beer)

    # ── Print results ─────────────────────────────────────────────────
    for i, b in enumerate(result.beers, 1):
        print(f"\n  Beer {i}:")
        print(f"    Name:    {b.beer_name}")
        print(f"    Brewery: {b.brewery}")
        print(f"    Style:   {b.style}")
        print(f"    ABV:     {b.abv}")
        print(f"    Rating:  {b.rating_score}")
        print(f"    Reviews: {b.num_reviews}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("beeradvocate")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = BeerSearchRequest()
            result = beeradvocate_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.beers)} beers")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
