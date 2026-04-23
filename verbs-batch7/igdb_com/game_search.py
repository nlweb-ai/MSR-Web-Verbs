"""
Auto-generated Playwright script (Python)
IGDB – Search games

Uses CDP-launched Chrome to avoid bot detection.
Extracts game data from React server-side JSON embedded in the search page.
"""

import os, sys, shutil, json, urllib.parse
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GameSearchRequest:
    query: str = "The Legend of Zelda"
    max_results: int = 5


@dataclass
class Game:
    title: str = ""
    release_year: str = ""
    platforms: str = ""
    category: str = ""


@dataclass
class GameSearchResult:
    games: List[Game] = field(default_factory=list)


def game_search(page: Page, request: GameSearchRequest) -> GameSearchResult:
    """Search IGDB for games and extract results from embedded JSON."""
    print(f"  Query: {request.query}")
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Navigate to IGDB search")
    q = urllib.parse.quote_plus(request.query)
    page.goto(
        f"https://www.igdb.com/search?type=1&q={q}",
        wait_until="domcontentloaded",
    )
    page.wait_for_timeout(8000)

    checkpoint("Extract game data from JSON")
    result = GameSearchResult()

    items = page.evaluate(
        r"""(max) => {
            const el = document.querySelector('script.js-react-on-rails-component[data-component-name="GameEntries"]');
            if (!el) return [];
            const data = JSON.parse(el.textContent);
            if (!data.games) return [];
            return data.games.slice(0, max).map(g => ({
                title: g.name || '',
                release_year: g.release_date ? g.release_date.split('-')[0] : '',
                platforms: (g.simple_platforms || []).map(p => p[0]).join(', '),
                category: g.category ? g.category.name : ''
            }));
        }""",
        request.max_results,
    )

    for item in items:
        g = Game()
        g.title = item.get("title", "")
        g.release_year = item.get("release_year", "")
        g.platforms = item.get("platforms", "")
        g.category = item.get("category", "")
        result.games.append(g)

    for i, g in enumerate(result.games):
        print(f"  Game {i + 1}:")
        print(f"    Title:    {g.title}")
        print(f"    Year:     {g.release_year}")
        print(f"    Platforms: {g.platforms}")
        print(f"    Category: {g.category}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("igdb")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = GameSearchRequest()
            result = game_search(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.games)} games")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
