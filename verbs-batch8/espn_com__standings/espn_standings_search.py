"""
ESPN – Get current league standings

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
class EspnStandingsSearchRequest:
    sport: str = "nba"
    max_results: int = 15


@dataclass
class EspnStandingsItem:
    team_name: str = ""
    wins: str = ""
    losses: str = ""
    ties: str = ""
    win_percentage: str = ""
    games_behind: str = ""
    division: str = ""
    conference: str = ""


@dataclass
class EspnStandingsSearchResult:
    items: List[EspnStandingsItem] = field(default_factory=list)


# Get current league standings from ESPN.
def espn_standings_search(page: Page, request: EspnStandingsSearchRequest) -> EspnStandingsSearchResult:
    """Get current league standings from ESPN."""
    print(f"  Sport: {request.sport}\n")

    url = f"https://www.espn.com/{request.sport}/standings"
    print(f"Loading {url}...")
    checkpoint("Navigate to ESPN standings page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = EspnStandingsSearchResult()

    checkpoint("Extract standings table")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();
        
        // ESPN splits standings into name column + stats table
        // Find team name links first
        const teamLinks = document.querySelectorAll('a[href*="/team/"]');
        const teamNames = [];
        for (const a of teamLinks) {
            const name = a.innerText.trim();
            if (name.length >= 2 && name.length <= 40 && !seen.has(name)) {
                seen.add(name);
                teamNames.push(name);
            }
        }
        
        // Now find stats rows from the stats table
        const tables = document.querySelectorAll('table');
        let statsRows = [];
        for (const table of tables) {
            const rows = table.querySelectorAll('tbody tr');
            if (rows.length >= 5) {
                // Check if first row has numeric cells
                const firstRowCells = rows[0].querySelectorAll('td');
                if (firstRowCells.length >= 2) {
                    const firstVal = firstRowCells[0].textContent.trim();
                    if (firstVal.match(/^\\d+$/)) {
                        statsRows = Array.from(rows);
                        break;
                    }
                }
            }
        }
        
        // Merge team names with stats
        const count = Math.min(teamNames.length, statsRows.length, max);
        for (let i = 0; i < count; i++) {
            const cells = statsRows[i].querySelectorAll('td');
            const vals = Array.from(cells).map(c => c.textContent.trim());
            
            const wins = vals[0] || '';
            const losses = vals[1] || '';
            const pct = vals.find(v => v.match(/^\\.\\d{3}$/)) || '';
            const gb = vals.find((v, idx) => idx >= 2 && (v === '-' || v.match(/^\\d+(\\.\\d)?$/))) || '';
            
            items.push({
                team_name: teamNames[i],
                wins, losses, ties: '',
                win_percentage: pct,
                games_behind: gb,
                division: '', conference: ''
            });
        }
        
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = EspnStandingsItem()
        item.team_name = d.get("team_name", "")
        item.wins = d.get("wins", "")
        item.losses = d.get("losses", "")
        item.ties = d.get("ties", "")
        item.win_percentage = d.get("win_percentage", "")
        item.games_behind = d.get("games_behind", "")
        item.division = d.get("division", "")
        item.conference = d.get("conference", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Team {i}:")
        print(f"    Name:       {item.team_name}")
        print(f"    W-L-T:      {item.wins}-{item.losses}-{item.ties}")
        print(f"    Win%:       {item.win_percentage}")
        print(f"    GB:         {item.games_behind}")
        print(f"    Division:   {item.division}")
        print(f"    Conference: {item.conference}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("espn_standings")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = EspnStandingsSearchRequest()
            result = espn_standings_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} teams")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
