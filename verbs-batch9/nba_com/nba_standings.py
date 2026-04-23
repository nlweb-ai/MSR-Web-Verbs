"""
Playwright script (Python) — NBA Standings
Browse NBA standings for the Eastern Conference.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class NBARequest:
    conference: str = "eastern"


@dataclass
class TeamStanding:
    team: str = ""
    wins: str = ""
    losses: str = ""
    win_pct: str = ""
    games_behind: str = ""
    streak: str = ""


@dataclass
class NBAResult:
    teams: List[TeamStanding] = field(default_factory=list)


# Browses NBA standings and extracts team name, wins, losses,
# win percentage, games behind, and streak.
def get_nba_standings(page: Page, request: NBARequest) -> NBAResult:
    url = "https://www.nba.com/standings"
    print(f"Loading {url}...")
    checkpoint("Navigate to NBA standings")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(10000)

    result = NBAResult()

    checkpoint("Extract standings table")
    js_code = """() => {
        const results = [];
        const rows = document.querySelectorAll('table tbody tr, [class*="standings"] tr');
        for (const row of rows) {
            const cells = row.querySelectorAll('td, th');
            if (cells.length < 5) continue;
            let team = cells[0] ? cells[0].textContent.trim() : '';
            if (!team || team === 'Team') continue;
            // Strip seed number prefix and clinch code suffix
            team = team.replace(/^\\d+/, '').replace(/\\s*-\\s*[a-z]+$/i, '').trim();
            results.push({
                team,
                wins: cells[1] ? cells[1].textContent.trim() : '',
                losses: cells[2] ? cells[2].textContent.trim() : '',
                win_pct: cells[3] ? cells[3].textContent.trim() : '',
                games_behind: cells[4] ? cells[4].textContent.trim() : '',
                streak: cells.length > 12 ? cells[12].textContent.trim() : '',
            });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code)

    for d in items_data:
        item = TeamStanding()
        item.team = d.get("team", "")
        item.wins = d.get("wins", "")
        item.losses = d.get("losses", "")
        item.win_pct = d.get("win_pct", "")
        item.games_behind = d.get("games_behind", "")
        item.streak = d.get("streak", "")
        result.teams.append(item)

    print(f"\nFound {len(result.teams)} teams:")
    for i, t in enumerate(result.teams, 1):
        print(f"  {i}. {t.team}: {t.wins}-{t.losses} ({t.win_pct}) GB: {t.games_behind} Streak: {t.streak}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("nba")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = get_nba_standings(page, NBARequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.teams)} teams")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
