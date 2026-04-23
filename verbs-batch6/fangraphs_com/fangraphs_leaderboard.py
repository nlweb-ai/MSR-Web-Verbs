"""
Auto-generated Playwright script (Python)
FanGraphs – MLB WAR Leaderboard

Generated on: 2026-04-18T05:19:52.459Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class LeaderboardRequest:
    max_results: int = 5


@dataclass
class Player:
    name: str = ""
    team: str = ""
    war: str = ""
    avg: str = ""
    hr: str = ""
    rbi: str = ""


@dataclass
class LeaderboardResult:
    players: list = field(default_factory=list)


def fangraphs_leaderboard(page: Page, request: LeaderboardRequest) -> LeaderboardResult:
    """Get top WAR leaders from FanGraphs leaderboard."""
    print(f"  Top {request.max_results} by WAR\n")

    # ── Step 1: Navigate to FanGraphs leaderboard ─────────────────────
    url = "https://www.fangraphs.com/leaders/major-league?pos=all&stats=bat&lg=all&qual=y&type=8&season=2025&month=0&season1=2025"
    print(f"Loading FanGraphs leaderboard...")
    checkpoint("Navigate to FanGraphs leaderboard")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Step 2: Extract top players from the page text ────────────────
    checkpoint("Extract WAR leaders")
    players_data = page.evaluate(r"""(maxPlayers) => {
        const text = document.body.innerText;
        const results = [];

        // The leaderboard data appears as lines like:
        // "1\tAaron Judge\tNYY\t152\t679\t53\t137\t114\t12\t18.3%\t23.6%\t.357\t.376\t.331\t.457\t.688\t.463\t.459\t204\t-4.1\t79.5\t-3.8\t10.1"
        // Headers: #, Name, Team, G, PA, HR, R, RBI, SB, BB%, K%, ISO, BABIP, AVG, OBP, SLG, wOBA, xwOBA, wRC+, BsR, Off, Def, WAR

        // Split by lines and look for numbered player rows
        const lines = text.split('\n');
        for (const line of lines) {
            if (results.length >= maxPlayers) break;
            // Match lines starting with a rank number
            const match = line.match(/^(\d+)\s+(.+?)\s+([A-Z]{2,3})\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)/);
            if (match) {
                const rank = parseInt(match[1]);
                const name = match[2].trim();
                const team = match[3];
                const hr = match[6];
                const rbi = match[8];

                // Extract AVG and WAR from the full line
                // AVG is the 13th field, WAR is the last field
                const parts = line.trim().split(/\s+/);
                let avg = '';
                let war = '';
                // Find .xxx patterns for AVG (batting average)
                for (let i = 0; i < parts.length; i++) {
                    if (/^\.\d{3}$/.test(parts[i]) && !avg) {
                        // Skip ISO and BABIP, take the first .xxx after those
                        // The order is: ISO, BABIP, AVG, OBP, SLG
                        // Count .xxx occurrences
                    }
                }
                // Simpler: AVG is typically around position 12-14 in the tab-separated data
                // WAR is the last number
                const allNums = line.match(/[\d.-]+/g);
                if (allNums && allNums.length > 5) {
                    war = allNums[allNums.length - 1];
                }
                // AVG: look for pattern like ".331" or ".295"
                const avgMatches = line.match(/\.\d{3}/g);
                if (avgMatches && avgMatches.length >= 3) {
                    avg = avgMatches[2]; // 3rd .xxx is AVG (after ISO and BABIP)
                }

                results.push({ rank, name, team, hr, rbi, avg, war });
            }
        }
        return results;
    }""", request.max_results)

    result = LeaderboardResult(
        players=[Player(
            name=p['name'], team=p['team'], war=p['war'],
            avg=p['avg'], hr=p['hr'], rbi=p['rbi']
        ) for p in players_data]
    )

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("FanGraphs: Top WAR Leaders (2025)")
    print("=" * 60)
    for p in players_data:
        print(f"\n  #{p['rank']} {p['name']} ({p['team']})")
        print(f"     WAR: {p['war']}  |  AVG: {p['avg']}  |  HR: {p['hr']}  |  RBI: {p['rbi']}")
    print(f"\n  Total: {len(result.players)} players")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("fangraphs_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = fangraphs_leaderboard(page, LeaderboardRequest())
            print(f"\nReturned {len(result.players)} players")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
