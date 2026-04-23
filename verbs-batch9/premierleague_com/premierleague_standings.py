"""
Playwright script (Python) — Premier League Standings
Browse Premier League standings table.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class PremierLeagueRequest:
    top_n: int = 10


@dataclass
class TeamStanding:
    position: str = ""
    team: str = ""
    played: str = ""
    won: str = ""
    drawn: str = ""
    lost: str = ""
    goals_for: str = ""
    goals_against: str = ""
    goal_diff: str = ""
    points: str = ""


@dataclass
class PremierLeagueResult:
    teams: List[TeamStanding] = field(default_factory=list)


# Extracts Premier League standings with position, team, played,
# won, drawn, lost, GF, GA, GD, and points.
def get_pl_standings(page: Page, request: PremierLeagueRequest) -> PremierLeagueResult:
    url = "https://www.premierleague.com/tables"
    print(f"Loading {url}...")
    checkpoint("Navigate to Premier League standings")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)

    result = PremierLeagueResult()

    checkpoint("Extract standings table")
    js_code = """(max) => {
        const results = [];
        const rows = document.querySelectorAll('tr');
        for (const row of rows) {
            if (results.length >= max) break;
            const text = row.innerText.trim();
            const parts = text.split(/\\t|\\n/).map(s => s.trim()).filter(s => s.length > 0);
            // A valid standings row has a position number, team name, and stats
            if (parts.length < 5) continue;
            const posMatch = parts[0].match(/^(\\d{1,2})$/);
            if (!posMatch) continue;

            const position = posMatch[1];
            // Team name is usually the longest non-numeric part
            let team = '';
            for (const p of parts) {
                if (p.length > team.length && isNaN(p) && !p.match(/^[+-]?\\d+$/)) team = p;
            }
            if (!team || team.length < 2) continue;

            // Extract numeric stats from the remaining parts
            const nums = parts.filter(p => p.match(/^-?\\d+$/)).map(Number);
            // Typical order: position, played, won, drawn, lost, GF, GA, GD, points
            results.push({
                position,
                team,
                played: nums.length > 1 ? String(nums[1]) : '',
                won: nums.length > 2 ? String(nums[2]) : '',
                drawn: nums.length > 3 ? String(nums[3]) : '',
                lost: nums.length > 4 ? String(nums[4]) : '',
                goals_for: nums.length > 5 ? String(nums[5]) : '',
                goals_against: nums.length > 6 ? String(nums[6]) : '',
                goal_diff: nums.length > 7 ? String(nums[7]) : '',
                points: nums.length > 8 ? String(nums[8]) : '',
            });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.top_n)

    for d in items_data:
        item = TeamStanding()
        item.position = d.get("position", "")
        item.team = d.get("team", "")
        item.played = d.get("played", "")
        item.won = d.get("won", "")
        item.drawn = d.get("drawn", "")
        item.lost = d.get("lost", "")
        item.goals_for = d.get("goals_for", "")
        item.goals_against = d.get("goals_against", "")
        item.goal_diff = d.get("goal_diff", "")
        item.points = d.get("points", "")
        result.teams.append(item)

    print(f"\nTop {len(result.teams)} teams:")
    for t in result.teams:
        print(f"  {t.position}. {t.team}: {t.played}P {t.won}W {t.drawn}D {t.lost}L GD:{t.goal_diff} Pts:{t.points}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("premierleague")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = get_pl_standings(page, PremierLeagueRequest())
            print("\n=== DONE ===")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
