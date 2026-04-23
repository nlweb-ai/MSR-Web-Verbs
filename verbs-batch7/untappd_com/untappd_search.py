"""
Auto-generated Playwright script (Python)
Untappd – Beer Search

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class SearchRequest:
    search_query: str = "IPA"
    max_results: int = 5


@dataclass
class BeerResult:
    name: str = ""
    brewery: str = ""
    style: str = ""
    abv: str = ""
    ibu: str = ""
    rating: str = ""


@dataclass
class SearchResult:
    beers: List[BeerResult] = field(default_factory=list)


def untappd_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search Untappd for beers."""
    print(f"  Query: {request.search_query}\n")

    url = f"https://untappd.com/search?q={request.search_query}&type=beer"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = SearchResult()

    checkpoint("Extract beer results")
    js_code = r"""(max) => {
        const lines = document.body.innerText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find start - after "Lowest ABV" sort option
        let startIdx = 0;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === 'Lowest ABV') { startIdx = i + 1; break; }
        }
        const beers = [];
        let i = startIdx;
        while (i < lines.length && beers.length < max) {
            const name = lines[i]; i++;
            if (!name || name === 'Please sign in to view more.') break;
            let brewery = '', style = '', abv = '', ibu = '', rating = '';
            if (i < lines.length) { brewery = lines[i]; i++; }
            if (i < lines.length) { style = lines[i]; i++; }
            if (i < lines.length && lines[i].includes('ABV')) { abv = lines[i]; i++; }
            if (i < lines.length && lines[i].includes('IBU')) { ibu = lines[i]; i++; }
            if (i < lines.length && /^\([\d.]+\)$/.test(lines[i])) {
                rating = lines[i].replace(/[()]/g, ''); i++;
            }
            beers.push({name, brewery, style, abv, ibu, rating});
        }
        return beers;
    }"""
    beers_data = page.evaluate(js_code, request.max_results)

    for bd in beers_data:
        b = BeerResult()
        b.name = bd.get("name", "")
        b.brewery = bd.get("brewery", "")
        b.style = bd.get("style", "")
        b.abv = bd.get("abv", "")
        b.ibu = bd.get("ibu", "")
        b.rating = bd.get("rating", "")
        result.beers.append(b)

    for i, b in enumerate(result.beers, 1):
        print(f"\n  Beer {i}:")
        print(f"    Name:    {b.name}")
        print(f"    Brewery: {b.brewery}")
        print(f"    Style:   {b.style}")
        print(f"    ABV:     {b.abv}")
        print(f"    IBU:     {b.ibu}")
        print(f"    Rating:  {b.rating}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("untappd")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = untappd_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.beers)} beers")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
