"""
Auto-generated Playwright script (Python)
IMDb – Top Box Office

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
class BoxOfficeRequest:
    max_results: int = 10


@dataclass
class Movie:
    title: str = ""
    weekend_gross: str = ""
    total_gross: str = ""
    weeks_released: str = ""


@dataclass
class BoxOfficeResult:
    movies: List[Movie] = field(default_factory=list)


def box_office(page: Page, request: BoxOfficeRequest) -> BoxOfficeResult:
    """Extract the current top box office movies from IMDb."""
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Navigate to IMDb box office")
    page.goto("https://www.imdb.com/chart/boxoffice", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract box office data")
    result = BoxOfficeResult()

    items = page.evaluate(
        r"""(max) => {
            const rows = document.querySelectorAll('li.ipc-metadata-list-summary-item');
            const results = [];
            for (let i = 0; i < rows.length && results.length < max; i++) {
                // Use anchor for title - skip image anchors (empty text)
                const anchors = rows[i].querySelectorAll('a[href*="/title/"]');
                let title = '';
                for (const a of anchors) {
                    const t = a.textContent.trim();
                    if (t) { title = t; break; }
                }
                if (!title) continue;

                // Use innerText lines for structured data
                const lines = rows[i].innerText.split('\n').map(l => l.trim()).filter(Boolean);
                let weekendGross = '', totalGross = '', weeksReleased = '';
                for (const line of lines) {
                    if (line.startsWith('Weekend Gross:')) weekendGross = line.replace('Weekend Gross:', '').trim();
                    else if (line.startsWith('Total Gross:')) totalGross = line.replace('Total Gross:', '').trim();
                    else if (line.startsWith('Weeks Released:')) weeksReleased = line.replace('Weeks Released:', '').trim();
                }

                results.push({title, weekend_gross: weekendGross, total_gross: totalGross, weeks_released: weeksReleased});
            }
            return results;
        }""",
        request.max_results,
    )

    for item in items:
        m = Movie()
        m.title = item.get("title", "")
        m.weekend_gross = item.get("weekend_gross", "")
        m.total_gross = item.get("total_gross", "")
        m.weeks_released = item.get("weeks_released", "")
        result.movies.append(m)

    for i, m in enumerate(result.movies):
        print(f"  #{i + 1}:")
        print(f"    Title:          {m.title}")
        print(f"    Weekend Gross:  {m.weekend_gross}")
        print(f"    Total Gross:    {m.total_gross}")
        print(f"    Weeks Released: {m.weeks_released}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("imdb_boxoffice")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = BoxOfficeRequest()
            result = box_office(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.movies)} movies")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
