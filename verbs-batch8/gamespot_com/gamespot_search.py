"""
GameSpot – Search for video game reviews by keyword

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
class GamespotSearchRequest:
    search_query: str = "zelda"
    max_results: int = 5


@dataclass
class GamespotResultItem:
    game_title: str = ""
    platform: str = ""
    score: str = ""
    review_date: str = ""
    reviewer: str = ""
    summary: str = ""


@dataclass
class GamespotSearchResult:
    items: List[GamespotResultItem] = field(default_factory=list)


# Search for video game reviews on GameSpot by keyword.
def gamespot_search(page: Page, request: GamespotSearchRequest) -> GamespotSearchResult:
    """Search for video game reviews on GameSpot."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://www.gamespot.com/search/?q={query}"
    print(f"Loading {url}...")
    checkpoint("Navigate to GameSpot search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = GamespotSearchResult()

    checkpoint("Extract game search result listings")
    js_code = """(max) => {
        const cards = document.querySelectorAll('[class*="search-result"], article, [class*="card"], [class*="media-body"], li[class*="result"]');
        const items = [];
        for (const card of cards) {
            if (items.length >= max) break;
            const titleEl = card.querySelector('h2 a, h3 a, h4 a, [class*="title"] a, a[class*="title"]');
            const platformEl = card.querySelector('[class*="platform"], [class*="system"], span[class*="deck"]');
            const scoreEl = card.querySelector('[class*="score"], [class*="rating"], [class*="review-ring"]');
            const dateEl = card.querySelector('time, [class*="date"], [class*="time"]');
            const reviewerEl = card.querySelector('[class*="author"], [class*="byline"]');
            const summaryEl = card.querySelector('p, [class*="deck"], [class*="description"], [class*="body"]');

            const game_title = titleEl ? titleEl.textContent.trim() : '';
            const platform = platformEl ? platformEl.textContent.trim() : '';
            const score = scoreEl ? scoreEl.textContent.trim() : '';
            const review_date = dateEl ? (dateEl.getAttribute('datetime') || dateEl.textContent.trim()) : '';
            const reviewer = reviewerEl ? reviewerEl.textContent.trim().replace(/^[Bb]y\s*/, '') : '';
            const summary = summaryEl ? summaryEl.textContent.trim() : '';

            if (game_title) {
                items.push({game_title, platform, score, review_date, reviewer, summary});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = GamespotResultItem()
        item.game_title = d.get("game_title", "")
        item.platform = d.get("platform", "")
        item.score = d.get("score", "")
        item.review_date = d.get("review_date", "")
        item.reviewer = d.get("reviewer", "")
        item.summary = d.get("summary", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Result {i}:")
        print(f"    Title:    {item.game_title}")
        print(f"    Platform: {item.platform}")
        print(f"    Score:    {item.score}")
        print(f"    Date:     {item.review_date}")
        print(f"    Reviewer: {item.reviewer}")
        print(f"    Summary:  {item.summary[:100]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("gamespot")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = GamespotSearchRequest()
            result = gamespot_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} game results")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
