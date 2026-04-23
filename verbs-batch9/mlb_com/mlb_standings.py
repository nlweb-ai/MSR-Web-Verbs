"""
Playwright script (Python) — MLB Standings
Browse MLB standings for the American League.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MLBRequest:
    league: str = "american-league"


@dataclass
class TeamStanding:
    team: str = ""
    wins: str = ""
    losses: str = ""
    win_pct: str = ""
    games_behind: str = ""
    last_10: str = ""


@dataclass
class MLBResult:
    teams: List[TeamStanding] = field(default_factory=list)


# Browses MLB standings for a league and extracts team name,
# wins, losses, win percentage, games behind, and last 10 record.
def get_mlb_standings(page: Page, request: MLBRequest) -> MLBResult:
    url = f"https://www.mlb.com/standings/{request.league}"
    print(f"Loading {url}...")
    checkpoint("Navigate to MLB standings")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(10000)

    result = MLBResult()

    checkpoint("Extract standings table")
    js_code = """() => {
        const results = [];
        const rows = document.querySelectorAll('table tbody tr, [class*="standings"] tr');
        for (const row of rows) {
            const cells = row.querySelectorAll('td, th');
            if (cells.length < 7) continue;
            const team = cells[0] ? cells[0].textContent.trim() : '';
            if (!team || team === 'Team') continue;
            // Skip division header rows
            const w = cells[1] ? cells[1].textContent.trim() : '';
            if (w === 'W') continue;
            results.push({
                team,
                wins: w,
                losses: cells[2] ? cells[2].textContent.trim() : '',
                win_pct: cells[3] ? cells[3].textContent.trim() : '',
                games_behind: cells[4] ? cells[4].textContent.trim() : '',
                last_10: cells[6] ? cells[6].textContent.trim() : '',
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
        item.last_10 = d.get("last_10", "")
        result.teams.append(item)

    print(f"\nFound {len(result.teams)} teams:")
    for i, t in enumerate(result.teams, 1):
        print(f"  {i}. {t.team}: {t.wins}-{t.losses} ({t.win_pct}) GB: {t.games_behind} L10: {t.last_10}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("mlb")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = get_mlb_standings(page, MLBRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.teams)} teams")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
