"""
Auto-generated Playwright script (Python)
Flashscore – Extract today's soccer matches

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
class MatchRequest:
    max_results: int = 5


@dataclass
class Match:
    home_team: str = ""
    away_team: str = ""
    score: str = ""
    league: str = ""
    status: str = ""


@dataclass
class MatchResult:
    matches: List[Match] = field(default_factory=list)


def flashscore_matches(page: Page, request: MatchRequest) -> MatchResult:
    """Extract today's soccer matches from Flashscore."""
    print("  Loading Flashscore...\n")

    checkpoint("Navigate to Flashscore")
    page.goto("https://www.flashscore.com/", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Dismiss cookie banner
    page.evaluate(r"""() => {
        const btn = document.querySelector('#onetrust-accept-btn-handler');
        if (btn) btn.click();
    }""")
    page.wait_for_timeout(1000)

    checkpoint("Extract matches")
    result = MatchResult()

    matches_data = page.evaluate(
        r"""(max) => {
            // All match and header rows are siblings under .sportName
            const container = document.querySelector('.sportName.soccer');
            if (!container) return [];

            const children = container.children;
            let currentLeague = '';
            const items = [];

            for (let i = 0; i < children.length && items.length < max; i++) {
                const el = children[i];

                // Check if this is a league header
                const leagueEl = el.querySelector('[data-testid="wcl-headerLeague"]');
                if (leagueEl) {
                    // Extract just league name and country, strip "Standings" etc.
                    const raw = leagueEl.textContent.trim().replace(/\s+/g, ' ');
                    // Format: "Premier LeagueENGLAND: Standings" -> split at uppercase country
                    const parts = raw.match(/^(.+?)([A-Z]{2,}.*?):\s*.*$/);
                    currentLeague = parts ? (parts[1].trim() + ' - ' + parts[2].trim()) : raw;
                    continue;
                }

                // Check if this is a match row
                if (!el.classList.contains('event__match')) continue;

                const home = el.querySelector('.event__homeParticipant [data-testid="wcl-scores-simple-text-01"]');
                const away = el.querySelector('.event__awayParticipant [data-testid="wcl-scores-simple-text-01"]');
                const scoreHome = el.querySelector('.event__score--home');
                const scoreAway = el.querySelector('.event__score--away');
                const stage = el.querySelector('.event__stage--block');

                items.push({
                    home_team: home ? home.textContent.trim() : '',
                    away_team: away ? away.textContent.trim() : '',
                    score_home: scoreHome ? scoreHome.textContent.trim() : '-',
                    score_away: scoreAway ? scoreAway.textContent.trim() : '-',
                    status: stage ? stage.textContent.trim() : '',
                    league: currentLeague
                });
            }
            return items;
        }""",
        request.max_results,
    )

    for d in matches_data:
        m = Match()
        m.home_team = d.get("home_team", "")
        m.away_team = d.get("away_team", "")
        m.score = f"{d.get('score_home', '-')} - {d.get('score_away', '-')}"
        m.league = d.get("league", "")
        m.status = d.get("status", "")
        result.matches.append(m)

    for i, m in enumerate(result.matches, 1):
        print(f"\n  Match {i}:")
        print(f"    League:    {m.league}")
        print(f"    Home:      {m.home_team}")
        print(f"    Away:      {m.away_team}")
        print(f"    Score:     {m.score}")
        print(f"    Status:    {m.status}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("flashscore")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = MatchRequest()
            result = flashscore_matches(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.matches)} matches")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
