"""
Playwright script (Python) — NFL Standings
Browse NFL standings for the AFC.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class NFLRequest:
    conference: str = "AFC"


@dataclass
class TeamStanding:
    team: str = ""
    wins: str = ""
    losses: str = ""
    ties: str = ""
    win_pct: str = ""
    points_for: str = ""
    points_against: str = ""


@dataclass
class NFLResult:
    teams: List[TeamStanding] = field(default_factory=list)


# Browses NFL standings and extracts team name, division, wins,
# losses, ties, win percentage, and points for/against.
def get_nfl_standings(page: Page, request: NFLRequest) -> NFLResult:
    url = "https://www.nfl.com/standings/"
    print(f"Loading {url}...")
    checkpoint("Navigate to NFL standings")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(10000)

    result = NFLResult()

    checkpoint("Extract standings table")
    js_code = """() => {
        const results = [];
        const rows = document.querySelectorAll('table tbody tr, [class*="standings"] tr');
        for (const row of rows) {
            const cells = row.querySelectorAll('td, th');
            if (cells.length < 5) continue;
            const w = cells[1] ? cells[1].textContent.trim() : '';
            if (w === 'W') continue;
            // Get team name from fullname span, strip clinch codes
            const fullnameSpan = cells[0].querySelector('.d3-o-club-fullname');
            let team = fullnameSpan ? fullnameSpan.textContent.trim() : (cells[0] ? cells[0].textContent.trim() : '');
            team = team.replace(/\\s+[a-z*]+$/, '').trim();
            if (!team || team === 'Team') continue;
            results.push({
                team,
                wins: w,
                losses: cells[2] ? cells[2].textContent.trim() : '',
                ties: cells[3] ? cells[3].textContent.trim() : '',
                win_pct: cells[4] ? cells[4].textContent.trim() : '',
                points_for: cells.length > 5 ? cells[5].textContent.trim() : '',
                points_against: cells.length > 6 ? cells[6].textContent.trim() : '',
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
        item.ties = d.get("ties", "")
        item.win_pct = d.get("win_pct", "")
        item.points_for = d.get("points_for", "")
        item.points_against = d.get("points_against", "")
        result.teams.append(item)

    print(f"\nFound {len(result.teams)} teams:")
    for i, t in enumerate(result.teams, 1):
        print(f"  {i}. {t.team}: {t.wins}-{t.losses}-{t.ties} ({t.win_pct}) PF: {t.points_for} PA: {t.points_against}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("nfl")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = get_nfl_standings(page, NFLRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.teams)} teams")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
