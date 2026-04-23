"""
Reelgood – Genre Movie Search

Browse movies by genre on Reelgood and extract title, release year,
and detail URL from the movie grid.
"""

import os, sys, re, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws


@dataclass(frozen=True)
class Request:
    genre: str = "thriller"
    max_results: int = 5


@dataclass
class Movie:
    title: str = ""
    year: str = ""
    url: str = ""


@dataclass
class Result:
    movies: List[Movie] = field(default_factory=list)


def genre_movies(page, request: Request) -> Result:
    """Navigate to Reelgood genre page and extract movie listings."""
    genre_slug = request.genre.lower().replace(" ", "-")
    url = f"https://reelgood.com/movies/genre/{genre_slug}"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    data = page.evaluate(r"""(maxResults) => {
        const allCards = document.querySelectorAll('a[href*="/movie/"]');
        const results = [];
        for (const a of allCards) {
            const text = a.textContent.trim();
            if (text.includes('Promoted')) continue;
            const titleEl = a.querySelector('[data-testid="content-listing-title"]');
            const title = titleEl ? titleEl.textContent.trim() : '';
            if (!title) continue;
            const yearMatch = text.match(/\((\d{4})\)/);
            const year = yearMatch ? yearMatch[1] : '';
            results.push({
                title: title,
                year: year,
                url: a.href,
            });
            if (results.length >= maxResults) break;
        }
        return results;
    }""", request.max_results)

    result = Result()
    for item in data:
        result.movies.append(Movie(
            title=item.get("title", ""),
            year=item.get("year", ""),
            url=item.get("url", ""),
        ))
    return result


# ── Test ──────────────────────────────────────────────────────────────────────
def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("reelgood_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            req = Request(genre="thriller", max_results=5)
            result = genre_movies(page, req)
            print(f"\n=== Reelgood {req.genre.title()} Movies ===")
            for i, m in enumerate(result.movies, 1):
                print(f"  {i}. {m.title} ({m.year})")
                print(f"     {m.url}")
            if not result.movies:
                print("  (no results)")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
