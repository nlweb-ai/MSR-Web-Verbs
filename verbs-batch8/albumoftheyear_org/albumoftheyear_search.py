"""
Album of the Year – Browse highest-rated albums by year

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
class AlbumSearchRequest:
    year: str = "2024"
    max_results: int = 5


@dataclass
class AlbumItem:
    title: str = ""
    artist: str = ""
    aggregate_score: str = ""
    num_critic_reviews: str = ""
    user_score: str = ""
    genre: str = ""


@dataclass
class AlbumSearchResult:
    items: List[AlbumItem] = field(default_factory=list)


# Browse the highest-rated albums of a given year on Album of the Year.
def albumoftheyear_search(page: Page, request: AlbumSearchRequest) -> AlbumSearchResult:
    """Browse highest-rated albums for a given year."""
    print(f"  Year: {request.year}\n")

    url = f"https://www.albumoftheyear.org/ratings/6-highest-rated/{request.year}/1"
    print(f"Loading {url}...")
    checkpoint("Navigate to AOTY ratings page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = AlbumSearchResult()

    checkpoint("Extract album listings")
    js_code = """(max) => {
        const rows = document.querySelectorAll('.albumListRow, .albumBlock');
        const items = [];
        for (const row of rows) {
            if (items.length >= max) break;
            const titleEl = row.querySelector('.albumListTitle a, .albumTitle a');
            const artistEl = row.querySelector('.albumListArtist a, .artistTitle a');
            const scoreEl = row.querySelector('.scoreValue, .rating');
            const userScoreEl = row.querySelector('.userScore, .userRating');
            const genreEl = row.querySelector('.albumListGenre, .genre');
            const reviewCountEl = row.querySelector('.reviewCount, .ratingCount');

            const title = titleEl ? titleEl.textContent.trim() : '';
            const artist = artistEl ? artistEl.textContent.trim() : '';
            const score = scoreEl ? scoreEl.textContent.trim() : '';
            const userScore = userScoreEl ? userScoreEl.textContent.trim() : '';
            const genre = genreEl ? genreEl.textContent.trim() : '';
            const numReviews = reviewCountEl ? reviewCountEl.textContent.trim().replace(/[^\\d]/g, '') : '';

            if (title) {
                items.push({title, artist, aggregate_score: score, num_critic_reviews: numReviews, user_score: userScore, genre});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = AlbumItem()
        item.title = d.get("title", "")
        item.artist = d.get("artist", "")
        item.aggregate_score = d.get("aggregate_score", "")
        item.num_critic_reviews = d.get("num_critic_reviews", "")
        item.user_score = d.get("user_score", "")
        item.genre = d.get("genre", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Album {i}:")
        print(f"    Title:    {item.title}")
        print(f"    Artist:   {item.artist}")
        print(f"    Score:    {item.aggregate_score}")
        print(f"    Reviews:  {item.num_critic_reviews}")
        print(f"    User:     {item.user_score}")
        print(f"    Genre:    {item.genre}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("albumoftheyear")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = AlbumSearchRequest()
            result = albumoftheyear_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} albums")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
