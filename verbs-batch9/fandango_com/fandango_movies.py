"""
Playwright script (Python) — Fandango Movie Showtimes
Search for movies playing near a zip code on Fandango.com.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class FandangoSearchRequest:
    zip_code: str = "90210"
    max_results: int = 5


@dataclass
class MovieItem:
    title: str = ""
    rating: str = ""
    runtime: str = ""
    showtime: str = ""


@dataclass
class FandangoSearchResult:
    zip_code: str = ""
    items: List[MovieItem] = field(default_factory=list)


# Searches Fandango.com for movies playing near the given zip code and returns
# up to max_results movies with title, genre, runtime, score, and next showtime.
def search_fandango_movies(page: Page, request: FandangoSearchRequest) -> FandangoSearchResult:
    url = f"https://www.fandango.com/{request.zip_code}_movietimes"
    print(f"Loading {url}...")
    checkpoint("Navigate to Fandango showtimes")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = FandangoSearchResult(zip_code=request.zip_code)

    checkpoint("Extract movie listings")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        // Featured movie
        const featured = document.querySelector('section.featured-movie');
        if (featured) {
            const lines = featured.innerText.split('\\n').filter(l => l.trim());
            let title = '', runtime = '', rating = '', showtime = '';
            for (let i = 0; i < lines.length; i++) {
                const l = lines[i].trim();
                if (l === 'Featured Movie' || l === 'Rated:' || l === 'Runtime:' || l === '\u2022') continue;
                if (!title && l.length > 3 && l !== 'Buy Tickets') { title = l; continue; }
                if (l.match(/^(G|PG|PG-13|R|NC-17|Not Rated|NR)$/)) { rating = l; continue; }
                if (l.match(/\d+\s*hr/)) { runtime = l; continue; }
                if (l.match(/\d+:\d+/)) { showtime = l; continue; }
            }
            if (title && !seen.has(title)) {
                seen.add(title);
                results.push({title, runtime, rating, showtime});
            }
        }
        // Regular movies
        const lis = document.querySelectorAll('li.shared-movie-showtimes');
        for (const li of lis) {
            if (results.length >= max) break;
            const lines = li.innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 3) continue;
            const title = lines[0].trim();
            if (!title || title.length < 3 || seen.has(title)) continue;
            seen.add(title);
            let runtime = '', rating = '', showtime = '';
            for (let i = 1; i < lines.length; i++) {
                const l = lines[i].trim();
                if (l === 'Rated:' || l === 'Runtime:' || l === 'Standard' || l === 'Standard Format' || l === '\u2022') continue;
                if (l.match(/^(G|PG|PG-13|R|NC-17|Not Rated|NR)$/)) { rating = l; continue; }
                if (l.match(/\d+\s*hr/)) { runtime = l; continue; }
                if (l.match(/\d+:\d+[ap]?$/i)) { showtime = l; continue; }
            }
            results.push({title, runtime, rating, showtime});
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = MovieItem()
        item.title = d.get("title", "")
        item.rating = d.get("rating", "")
        item.runtime = d.get("runtime", "")
        item.showtime = d.get("showtime", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} movies near '{request.zip_code}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Rating: {item.rating}  Runtime: {item.runtime}")
        print(f"     Showtime: {item.showtime}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("fandango")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_fandango_movies(page, FandangoSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} movies")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
