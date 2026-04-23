"""
Rotten Tomatoes – Browse upcoming movie releases

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
class RottenTomatoesComingSoonSearchRequest:
    max_results: int = 10


@dataclass
class RottenTomatoesMovieItem:
    movie_title: str = ""
    tomatometer_score: str = ""
    audience_score: str = ""
    release_date: str = ""
    synopsis: str = ""
    critics_consensus: str = ""


@dataclass
class RottenTomatoesComingSoonSearchResult:
    items: List[RottenTomatoesMovieItem] = field(default_factory=list)


# Browse upcoming movie releases on Rotten Tomatoes.
def rottentomatoes_coming_soon_search(page: Page, request: RottenTomatoesComingSoonSearchRequest) -> RottenTomatoesComingSoonSearchResult:
    """Browse upcoming movie releases on Rotten Tomatoes."""
    print(f"  Fetching up to {request.max_results} upcoming movies\n")

    url = "https://www.rottentomatoes.com/browse/movies_coming_soon/"
    print(f"Loading {url}...")
    checkpoint("Navigate to Rotten Tomatoes coming soon page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = RottenTomatoesComingSoonSearchResult()

    checkpoint("Extract movie listings")
    js_code = """(max) => {
        const cards = document.querySelectorAll('[class*="discovery-tiles"] a, [class*="tile"], [class*="MovieCard"], [class*="movie-card"], [data-qa="discovery-media-list-item"]');
        const items = [];
        for (const card of cards) {
            if (items.length >= max) break;
            const titleEl = card.querySelector('[class*="title"], h2, h3, span[data-qa="discovery-media-list-item-title"]');
            const tomatometerEl = card.querySelector('[class*="tomatometer"], [data-qa="tomatometer"], score-pairs-deprecated, [slot="criticsScore"]');
            const audienceEl = card.querySelector('[class*="audience"], [data-qa="audience-score"], [slot="audienceScore"]');
            const dateEl = card.querySelector('[class*="date"], [class*="release"], time, [data-qa="discovery-media-list-item-start-date"]');
            const synopsisEl = card.querySelector('[class*="synopsis"], [class*="description"], p');
            const consensusEl = card.querySelector('[class*="consensus"], [class*="critic"]');

            const movie_title = titleEl ? titleEl.textContent.trim() : '';
            const tomatometer_score = tomatometerEl ? tomatometerEl.textContent.trim() : '';
            const audience_score = audienceEl ? audienceEl.textContent.trim() : '';
            const release_date = dateEl ? (dateEl.getAttribute('datetime') || dateEl.textContent.trim()) : '';
            const synopsis = synopsisEl ? synopsisEl.textContent.trim() : '';
            const critics_consensus = consensusEl ? consensusEl.textContent.trim() : '';

            if (movie_title) {
                items.push({movie_title, tomatometer_score, audience_score, release_date, synopsis, critics_consensus});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = RottenTomatoesMovieItem()
        item.movie_title = d.get("movie_title", "")
        item.tomatometer_score = d.get("tomatometer_score", "")
        item.audience_score = d.get("audience_score", "")
        item.release_date = d.get("release_date", "")
        item.synopsis = d.get("synopsis", "")
        item.critics_consensus = d.get("critics_consensus", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Movie {i}:")
        print(f"    Title:       {item.movie_title}")
        print(f"    Tomatometer: {item.tomatometer_score}")
        print(f"    Audience:    {item.audience_score}")
        print(f"    Release:     {item.release_date}")
        print(f"    Synopsis:    {item.synopsis[:100]}...")
        print(f"    Consensus:   {item.critics_consensus[:100]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("rottentomatoes")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = RottenTomatoesComingSoonSearchRequest()
            result = rottentomatoes_coming_soon_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} movies")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
