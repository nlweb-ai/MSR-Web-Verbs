"""
Box Office Mojo – Browse current weekend box office rankings

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
class BoxOfficeMojoSearchRequest:
    max_results: int = 10


@dataclass
class BoxOfficeMovieItem:
    rank: str = ""
    movie_title: str = ""
    weekend_gross: str = ""
    total_gross: str = ""
    weeks_in_release: str = ""
    distributor: str = ""


@dataclass
class BoxOfficeMojoSearchResult:
    items: List[BoxOfficeMovieItem] = field(default_factory=list)


# Browse the current weekend box office rankings on Box Office Mojo.
def boxofficemojo_search(page: Page, request: BoxOfficeMojoSearchRequest) -> BoxOfficeMojoSearchResult:
    """Browse current weekend box office rankings."""
    print(f"  Max results: {request.max_results}\n")

    url = "https://www.boxofficemojo.com/weekly/"
    print(f"Loading {url}...")
    checkpoint("Navigate to Box Office Mojo weekend chart")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = BoxOfficeMojoSearchResult()

    checkpoint("Extract box office rankings")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();
        
        // Find all table rows
        const rows = document.querySelectorAll('table tr');
        for (const row of rows) {
            if (items.length >= max) break;
            const cells = row.querySelectorAll('td');
            if (cells.length < 3) continue;
            
            const titleEl = row.querySelector('a[href*="/release/"], a[href*="/title/"]');
            if (!titleEl) continue;
            const title = titleEl.textContent.trim();
            if (!title || seen.has(title)) continue;
            seen.add(title);
            
            const cellTexts = Array.from(cells).map(c => c.textContent.trim());
            const rankText = cellTexts[0] || '';
            
            // Find money amounts
            let weekendGross = '';
            let totalGross = '';
            for (const t of cellTexts) {
                if (t.startsWith('$')) {
                    if (!weekendGross) weekendGross = t;
                    else totalGross = t;
                }
            }
            
            items.push({
                rank: rankText,
                movie_title: title,
                weekend_gross: weekendGross,
                total_gross: totalGross,
                weeks_in_release: '',
                distributor: ''
            });
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = BoxOfficeMovieItem()
        item.rank = d.get("rank", "")
        item.movie_title = d.get("movie_title", "")
        item.weekend_gross = d.get("weekend_gross", "")
        item.total_gross = d.get("total_gross", "")
        item.weeks_in_release = d.get("weeks_in_release", "")
        item.distributor = d.get("distributor", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Movie {i}:")
        print(f"    Rank:          {item.rank}")
        print(f"    Title:         {item.movie_title}")
        print(f"    Weekend Gross: {item.weekend_gross}")
        print(f"    Total Gross:   {item.total_gross}")
        print(f"    Weeks:         {item.weeks_in_release}")
        print(f"    Distributor:   {item.distributor}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("boxofficemojo")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = BoxOfficeMojoSearchRequest()
            result = boxofficemojo_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} movies")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
