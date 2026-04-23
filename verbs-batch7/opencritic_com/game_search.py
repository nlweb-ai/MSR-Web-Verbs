"""
OpenCritic – Game Search

Search OpenCritic for a game and extract: game title, top critic average
score, percent recommended, platforms, and release date.
Uses a search-then-navigate approach (type → Enter → game detail page).
"""

import os, sys, re, shutil
from dataclasses import dataclass
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws


@dataclass(frozen=True)
class Request:
    Game_Name: str = "Elden Ring"


@dataclass
class Result:
    title: str = ""
    top_critic_average: str = ""
    percent_recommended: str = ""
    platforms: str = ""
    release_date: str = ""


def game_search(page, request: Request) -> Result:
    """Search OpenCritic for a game and extract its details."""

    # Step 1: Navigate to OpenCritic
    page.goto("https://opencritic.com", wait_until="domcontentloaded")
    page.wait_for_timeout(4000)

    # Step 2: Type the game name into the search input and press Enter
    search = page.query_selector('input[type="search"], input[placeholder*="earch"]')
    if not search:
        return Result()
    search.click()
    page.keyboard.type(request.Game_Name, delay=50)
    page.wait_for_timeout(2000)
    page.keyboard.press("Enter")
    page.wait_for_timeout(5000)

    # Step 3: Extract game details from the game page
    data = page.evaluate(r"""() => {
        const title = document.querySelector('h1')?.textContent.trim() || '';

        // Score orbs: first = top critic average, second = percent recommended
        const scoreOrbs = document.querySelectorAll('.score-orb');
        const topCriticAverage = scoreOrbs[0]?.textContent.trim() || '';
        const percentRecommended = scoreOrbs[1]?.textContent.trim() || '';

        // Release date and platforms from body text
        const bodyText = document.body.innerText;
        const relMatch = bodyText.match(/Release Date:\s*(.+)/);
        let releaseDate = '';
        let platforms = '';
        if (relMatch) {
            const parts = relMatch[1].trim().split(' - ');
            releaseDate = parts[0]?.trim() || '';
            platforms = parts[1]?.trim() || '';
        }

        return { title, topCriticAverage, percentRecommended, releaseDate, platforms };
    }""")

    return Result(
        title=data.get("title", ""),
        top_critic_average=data.get("topCriticAverage", ""),
        percent_recommended=data.get("percentRecommended", ""),
        platforms=data.get("platforms", ""),
        release_date=data.get("releaseDate", ""),
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("opencritic_game_search")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            req = Request(Game_Name="Elden Ring")
            result = game_search(page, req)
            print(f"\nGame: {result.title}")
            print(f"Top Critic Average: {result.top_critic_average}")
            print(f"Percent Recommended: {result.percent_recommended}")
            print(f"Platforms: {result.platforms}")
            print(f"Release Date: {result.release_date}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
