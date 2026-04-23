"""
IMDb – Browse upcoming movie releases

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
class ImdbComingSoonSearchRequest:
    max_results: int = 10


@dataclass
class ImdbComingSoonItem:
    movie_title: str = ""
    release_date: str = ""
    genres: str = ""
    stars: str = ""
    director: str = ""
    synopsis: str = ""


@dataclass
class ImdbComingSoonSearchResult:
    items: List[ImdbComingSoonItem] = field(default_factory=list)


# Browse upcoming movie releases on IMDb.
def imdb_coming_soon_search(page: Page, request: ImdbComingSoonSearchRequest) -> ImdbComingSoonSearchResult:
    """Browse upcoming movie releases on IMDb."""
    print(f"  Max results: {request.max_results}\n")

    url = "https://www.imdb.com/calendar/"
    print(f"Loading {url}...")
    checkpoint("Navigate to IMDb coming soon page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = ImdbComingSoonSearchResult()

    checkpoint("Extract upcoming movie listings")
    js_code = r"""(max) => {
        const items = [];
        const seen = new Set();
        
        // Find links to title pages
        const links = document.querySelectorAll('a[href*="/title/tt"]');
        for (const a of links) {
            if (items.length >= max) break;
            const title = a.innerText.trim().split('\n')[0].trim();
            if (title.length < 2 || title.length > 150 || seen.has(title)) continue;
            // Skip dates and navigation text
            if (title.match(/^\w+\s+\d{1,2},\s+\d{4}$/)) continue;
            seen.add(title);
            
            const card = a.closest('li, div[class]') || a;
            const fullText = card.innerText.trim();
            const lines = fullText.split('\n').filter(l => l.trim());
            
            let releaseDate = '';
            let stars = '';
            for (const line of lines) {
                if (line.match(/\w+\s+\d{1,2},\s+\d{4}/)) releaseDate = line;
            }
            
            items.push({movie_title: title, release_date: releaseDate, genres: '', stars: '', director: '', synopsis: ''});
        }
        
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ImdbComingSoonItem()
        item.movie_title = d.get("movie_title", "")
        item.release_date = d.get("release_date", "")
        item.genres = d.get("genres", "")
        item.stars = d.get("stars", "")
        item.director = d.get("director", "")
        item.synopsis = d.get("synopsis", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Movie {i}:")
        print(f"    Title:    {item.movie_title}")
        print(f"    Release:  {item.release_date}")
        print(f"    Genres:   {item.genres}")
        print(f"    Stars:    {item.stars[:60]}")
        print(f"    Director: {item.director}")
        print(f"    Synopsis: {item.synopsis[:80]}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("imdb_coming_soon")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = ImdbComingSoonSearchRequest()
            result = imdb_coming_soon_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} upcoming movies")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
