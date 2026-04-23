"""
Auto-generated Playwright script (Python)
IMDb – Top Rated Movies (Top 250)

Generated on: 2026-04-18T14:43:53.806Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MovieRequest:
    max_results: int = 10


@dataclass
class Movie:
    rank: str = ""
    title: str = ""
    year: str = ""
    rating: str = ""
    votes: str = ""


@dataclass
class MovieResult:
    movies: List[Movie] = field(default_factory=list)


def imdb_top_rated(page: Page, request: MovieRequest) -> MovieResult:
    """Extract top rated movies from IMDb Top 250."""
    print(f"  Extracting top {request.max_results} movies\n")

    # ── Step 1: Navigate to IMDb Top 250 ──────────────────────────────
    print("Loading IMDb Top 250...")
    checkpoint("Navigate to IMDb Top 250")
    page.goto("https://www.imdb.com/chart/top/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # ── Step 2: Extract movie data from list items ────────────────────
    checkpoint("Extract top movies")
    items = page.evaluate(r"""(maxResults) => {
        const listItems = document.querySelectorAll('li.ipc-metadata-list-summary-item');
        return Array.from(listItems).slice(0, maxResults).map(li => {
            const rankEl = li.querySelector('[data-testid="title-list-item-ranking"]');
            const rank = rankEl ? rankEl.innerText.replace('#', '').trim() : '';

            const titleEl = li.querySelector('h3.ipc-title__text');
            const title = titleEl ? titleEl.innerText.trim() : '';

            // Metadata: year, runtime, rating
            const metaEl = li.querySelector('.cli-title-metadata');
            const metaParts = metaEl ? metaEl.innerText.split('\n').map(s => s.trim()) : [];
            const year = metaParts[0] || '';

            const ratingEl = li.querySelector('.ipc-rating-star--rating');
            const rating = ratingEl ? ratingEl.innerText.trim() : '';

            const votesEl = li.querySelector('.ipc-rating-star--voteCount');
            const votes = votesEl ? votesEl.innerText.replace(/[()]/g, '').trim() : '';

            return { rank, title, year, rating, votes };
        });
    }""", request.max_results)

    result = MovieResult(movies=[Movie(
        rank=m['rank'], title=m['title'], year=m['year'],
        rating=m['rating'], votes=m['votes']
    ) for m in items])

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("IMDb Top 250 Movies")
    print("=" * 70)
    for m in items:
        print(f"  #{m['rank']:>3}  {m['title']} ({m['year']})  —  {m['rating']}  ({m['votes']} votes)")
    print(f"\n  Total: {len(items)} movies")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("imdb_com__topRated")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = imdb_top_rated(page, MovieRequest())
            print(f"\nReturned {len(result.movies)} movies")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
