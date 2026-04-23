"""
Playwright script (Python) — OddsShark NFL Odds
Browse OddsShark for NFL game odds.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class OddsSharkRequest:
    sport: str = "nfl"
    max_results: int = 5


@dataclass
class GameOdds:
    teams: str = ""
    spread: str = ""
    over_under: str = ""
    game_time: str = ""


@dataclass
class OddsSharkResult:
    games: List[GameOdds] = field(default_factory=list)


# Browses OddsShark for NFL game odds and extracts teams,
# spread, over/under, moneyline, and game time.
def get_nfl_odds(page: Page, request: OddsSharkRequest) -> OddsSharkResult:
    url = f"https://www.oddsshark.com/{request.sport}/odds"
    print(f"Loading {url}...")
    checkpoint("Navigate to OddsShark NFL odds")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)

    result = OddsSharkResult()

    checkpoint("Extract game odds")
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Parse ticker games: Time, Channel, Team1, Team2, Spread1, Spread2, [Win%1, Win%2,] O/U
        // Also FINAL games: FINAL, Team1, Team2, Score1, Score2, Spread1, Spread2, O/U
        const timeRe = /^\\d{1,2}:\\d{2}\\s*(AM|PM)/i;
        const seen = new Set();
        let i = 0;
        // Skip header/nav until we hit FINAL or a time
        while (i < lines.length && !/^(FINAL|Yesterday|Today|Tomorrow)$/i.test(lines[i]) && !timeRe.test(lines[i])) i++;
        while (i < lines.length && results.length < max) {
            // Skip section markers
            if (/^(Yesterday|Today|Tomorrow|Previous|Next|NFL|NBA|MLB|NHL|FINAL)$/i.test(lines[i])) {
                if (lines[i] === 'FINAL') {
                    // Skip FINAL games (past results)
                    i++;
                    // Skip: Team1, Team2, Score1, Score2, Spread1, Spread2, O/U
                    i += 7;
                    continue;
                }
                i++;
                continue;
            }
            if (timeRe.test(lines[i])) {
                const game_time = lines[i];
                i++; // channel
                const channel = lines[i] || ''; i++;
                const team1 = lines[i] || ''; i++;
                const team2 = lines[i] || ''; i++;
                const spread1 = lines[i] || ''; i++;
                const spread2 = lines[i] || ''; i++;
                // Optional win percentages
                let ou = '';
                if (/%$/.test(lines[i])) {
                    i += 2; // skip both percentages
                }
                ou = lines[i] || ''; i++;
                const key = team1 + team2;
                if (seen.has(key)) continue;
                seen.add(key);
                results.push({ teams: team1 + ' vs ' + team2, spread: spread1 + ' / ' + spread2, over_under: ou, moneyline: '', game_time });
            } else {
                i++;
            }
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = GameOdds()
        item.teams = d.get("teams", "")
        item.spread = d.get("spread", "")
        item.over_under = d.get("over_under", "")
        item.game_time = d.get("game_time", "")
        result.games.append(item)

    print(f"\nFound {len(result.games)} games:")
    for i, g in enumerate(result.games, 1):
        print(f"  {i}. {g.teams}  Spread: {g.spread}  O/U: {g.over_under}  Time: {g.game_time}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("oddsshark")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = get_nfl_odds(page, OddsSharkRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.games)} games")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
