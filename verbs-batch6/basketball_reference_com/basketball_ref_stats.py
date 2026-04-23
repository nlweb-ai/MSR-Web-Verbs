"""
Auto-generated Playwright script (Python)
Basketball Reference – Player Stats
Player: "LeBron James"

Generated on: 2026-04-18T04:56:09.795Z
Recorded 3 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class PlayerRequest:
    player: str = "LeBron James"


@dataclass
class PlayerStats:
    player_name: str = ""
    ppg: str = ""
    rpg: str = ""
    apg: str = ""
    games_played: str = ""
    career_points: str = ""


def basketball_ref_search(page: Page, request: PlayerRequest) -> PlayerStats:
    """Search Basketball Reference for player career stats."""
    print(f"  Player: {request.player}\n")

    # ── Step 1: Search for the player ─────────────────────────────────
    search_url = f"https://www.basketball-reference.com/search/search.fcgi?search={quote_plus(request.player)}"
    print(f"Loading {search_url}...")
    checkpoint("Search Basketball Reference")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # ── Step 2: Navigate to player page ───────────────────────────────
    if "/players/" not in page.url:
        # On search results page — extract first player URL
        checkpoint("Click player from search results")
        player_url = page.evaluate(r"""() => {
            const items = document.querySelectorAll('.search-item-name a[href*="/players/"]');
            for (const a of items) {
                if (a.offsetParent !== null) return a.href;
            }
            // Fallback: any visible player link in content
            const content = document.querySelector('#content, main') || document.body;
            const links = content.querySelectorAll('a[href*="/players/"]');
            for (const a of links) {
                if (a.offsetParent !== null && a.innerText.length > 3) return a.href;
            }
            return '';
        }""")
        if player_url:
            page.goto(player_url, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
        else:
            print("No player found in search results.")
            return PlayerStats(player_name=request.player)

    # ── Step 3: Extract career per-game stats ─────────────────────────
    checkpoint("Extract career stats")
    stats = page.evaluate(r"""() => {
        const result = {};

        // Get player name from page
        const h1 = document.querySelector('h1');
        result.player_name = h1 ? h1.innerText.trim() : '';

        // Per-game stats table — career row is tfoot tr index 1 (index 0 is sub-header)
        const pgTable = document.querySelector('#per_game_stats');
        if (pgTable) {
            const rows = pgTable.querySelectorAll('tfoot tr');
            // Find the career row (firstCellText contains "Yrs")
            for (const row of rows) {
                const first = row.querySelector('[data-stat="year_id"]');
                if (first && first.innerText.includes('Yr')) {
                    const get = (stat) => {
                        const cell = row.querySelector(`[data-stat="${stat}"]`);
                        return cell ? cell.innerText.trim() : '';
                    };
                    result.ppg = get('pts_per_g');
                    result.rpg = get('trb_per_g');
                    result.apg = get('ast_per_g');
                    result.games = get('games');
                    break;
                }
            }
        }

        // Totals table — career total points
        const totTable = document.querySelector('#totals_stats');
        if (totTable) {
            const rows = totTable.querySelectorAll('tfoot tr');
            for (const row of rows) {
                const first = row.querySelector('[data-stat="year_id"]');
                if (first && first.innerText.includes('Yr')) {
                    const pts = row.querySelector('[data-stat="pts"]');
                    result.career_points = pts ? pts.innerText.trim() : '';
                    const trb = row.querySelector('[data-stat="trb"]');
                    result.career_rebounds = trb ? trb.innerText.trim() : '';
                    const ast = row.querySelector('[data-stat="ast"]');
                    result.career_assists = ast ? ast.innerText.trim() : '';
                    break;
                }
            }
        }

        return result;
    }""")

    result = PlayerStats(
        player_name=stats.get("player_name", request.player),
        ppg=stats.get("ppg", ""),
        rpg=stats.get("rpg", ""),
        apg=stats.get("apg", ""),
        games_played=stats.get("games", ""),
        career_points=stats.get("career_points", ""),
    )

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Basketball Reference: {result.player_name}")
    print("=" * 60)
    print(f"  Games Played:     {result.games_played}")
    print(f"  Points Per Game:  {result.ppg}")
    print(f"  Rebounds Per Game: {result.rpg}")
    print(f"  Assists Per Game: {result.apg}")
    print(f"  Career Points:    {result.career_points}")
    if stats.get("career_rebounds"):
        print(f"  Career Rebounds:  {stats['career_rebounds']}")
    if stats.get("career_assists"):
        print(f"  Career Assists:   {stats['career_assists']}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("basketball_ref")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = basketball_ref_search(page, PlayerRequest())
            print(f"\nReturned stats for {result.player_name}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
