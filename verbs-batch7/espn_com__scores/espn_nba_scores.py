"""
Auto-generated Playwright script (Python)
ESPN – NBA Scoreboard

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
class ScoreboardRequest:
    max_games: int = 5


@dataclass
class Game:
    away_team: str = ""
    home_team: str = ""
    away_score: str = ""
    home_score: str = ""
    status: str = ""
    series_info: str = ""


@dataclass
class ScoreboardResult:
    games: List[Game] = field(default_factory=list)


def espn_nba_scores(page: Page, request: ScoreboardRequest) -> ScoreboardResult:
    """Extract NBA game scores from ESPN scoreboard."""
    print(f"  Max games: {request.max_games}\n")

    # ── Navigate to scoreboard ────────────────────────────────────────
    url = "https://www.espn.com/nba/scoreboard"
    print(f"Loading {url}...")
    checkpoint("Navigate to ESPN NBA scoreboard")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = ScoreboardResult()

    # ── Extract game scores ───────────────────────────────────────────
    checkpoint("Extract game scores")
    games_data = page.evaluate(
        r"""(max) => {
            const cells = document.querySelectorAll('.ScoreboardScoreCell');
            const games = [];
            for (let i = 0; i < cells.length && games.length < max; i++) {
                const cell = cells[i];
                const teamEls = cell.querySelectorAll('.ScoreCell__TeamName');
                const scoreEls = cell.querySelectorAll('.ScoreCell__Score');
                const timeEl = cell.querySelector('.ScoreCell__Time');
                const seriesEl = cell.querySelector('.ScoreboardScoreCell__Note');

                const teams = Array.from(teamEls).map(el => el.textContent.trim());
                const scores = Array.from(scoreEls).map(el => el.textContent.trim());
                const status = timeEl ? timeEl.textContent.trim() : '';
                const series = seriesEl ? seriesEl.textContent.trim() : '';

                games.push({
                    away_team: teams[0] || '',
                    home_team: teams[1] || '',
                    away_score: scores[0] || '',
                    home_score: scores[1] || '',
                    status: status,
                    series_info: series
                });
            }
            return games;
        }""",
        request.max_games,
    )

    for d in games_data:
        game = Game()
        game.away_team = d.get("away_team", "")
        game.home_team = d.get("home_team", "")
        game.away_score = d.get("away_score", "")
        game.home_score = d.get("home_score", "")
        game.status = d.get("status", "")
        game.series_info = d.get("series_info", "")
        result.games.append(game)

    # ── Print results ─────────────────────────────────────────────────
    for i, g in enumerate(result.games, 1):
        print(f"\n  Game {i}:")
        print(f"    {g.away_team} {g.away_score} @ {g.home_team} {g.home_score}")
        print(f"    Status: {g.status}")
        print(f"    Series: {g.series_info}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("espn_scores")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = ScoreboardRequest()
            result = espn_nba_scores(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.games)} games")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
