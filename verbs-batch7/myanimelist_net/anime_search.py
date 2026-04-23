"""
MyAnimeList – Anime Search

Search MyAnimeList for an anime and extract the top result's details:
title, score, rank, episodes, aired dates, synopsis, and genres.
Uses a two-step approach: search → visit detail page.
"""

import os, sys, re, shutil, urllib.parse
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws


@dataclass(frozen=True)
class Request:
    query: str = "Steins;Gate"


@dataclass
class Result:
    title: str = ""
    score: str = ""
    rank: str = ""
    episodes: str = ""
    aired: str = ""
    synopsis: str = ""
    genres: List[str] = field(default_factory=list)


def anime_search(page, request: Request) -> Result:
    """Search MAL for an anime and extract top result details."""

    # Step 1: Search
    search_url = f"https://myanimelist.net/anime.php?q={urllib.parse.quote(request.query)}&cat=anime"
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Get first search result link
    first_href = page.evaluate(r"""() => {
        const rows = document.querySelectorAll('.js-categories-seasonal tr');
        for (const row of rows) {
            const link = row.querySelector('a.hoverinfo_trigger[href*="/anime/"]');
            if (link && link.href.match(/\/anime\/\d+\//)) {
                return link.href;
            }
        }
        return null;
    }""")

    if not first_href:
        return Result()

    # Step 2: Visit detail page
    page.goto(first_href, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)

    data = page.evaluate(r"""() => {
        const title = document.querySelector('h1.title-name strong')?.textContent.trim() ||
                      document.querySelector('h1')?.textContent.trim() || '';

        const score = document.querySelector('[itemprop="ratingValue"]')?.textContent.trim() || '';

        // Extract info from .spaceit_pad elements
        const spaceit = document.querySelectorAll('.spaceit_pad');
        const info = {};
        for (const s of spaceit) {
            const text = s.innerText.trim();
            const m = text.match(/^([\w\s]+?):\s*(.+)/s);
            if (m) info[m[1].trim()] = m[2].trim();
        }

        const rank = info['Ranked'] || '';
        const episodes = info['Episodes'] || '';
        const aired = info['Aired'] || '';

        const synopsis = document.querySelector('[itemprop="description"]')?.textContent.trim() || '';

        const genres = Array.from(document.querySelectorAll('[itemprop="genre"]'))
            .map(g => g.textContent.trim());

        return { title, score, rank, episodes, aired, synopsis, genres };
    }""")

    return Result(
        title=data.get("title", ""),
        score=data.get("score", ""),
        rank=data.get("rank", ""),
        episodes=data.get("episodes", ""),
        aired=data.get("aired", ""),
        synopsis=data.get("synopsis", ""),
        genres=data.get("genres", []),
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("mal_anime_search")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            req = Request(query="Steins;Gate")
            result = anime_search(page, req)
            print(f"\nAnime: {result.title}")
            print(f"Score: {result.score}")
            print(f"Rank: {result.rank}")
            print(f"Episodes: {result.episodes}")
            print(f"Aired: {result.aired}")
            print(f"Genres: {', '.join(result.genres)}")
            print(f"Synopsis: {result.synopsis[:200]}...")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
