"""
Playwright script (Python) — ESPN.com Standings
Navigate to the standings page for a league and extract top teams with wins/losses.

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class EspnStandingsRequest:
    league: str
    max_results: int


@dataclass(frozen=True)
class EspnTeamStanding:
    team_name: str
    wins: str
    losses: str


@dataclass(frozen=True)
class EspnStandingsResult:
    league: str
    teams: list[EspnTeamStanding]


# Navigates to the ESPN standings page for a given league and extracts
# up to max_results teams with team name, wins, and losses.
def get_espn_standings(
    page: Page,
    request: EspnStandingsRequest,
) -> EspnStandingsResult:
    league = request.league
    max_results = request.max_results

    print(f"  League: {league}")
    print(f"  Max results: {max_results}\n")

    results: list[EspnTeamStanding] = []

    try:
        # ── Navigate to standings ─────────────────────────────────────────
        print(f"Loading ESPN {league} standings...")
        url = f"https://www.espn.com/{league.lower()}/standings"
        checkpoint(f"Navigate to {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # ── Dismiss popups ────────────────────────────────────────────────
        for selector in [
            "button#onetrust-accept-btn-handler",
            "button:has-text('Accept')",
            "button:has-text('No, thanks')",
            "button:has-text('Close')",
        ]:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {selector}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        # ── STEP 1: Extract standings ─────────────────────────────────────
        print(f"STEP 1: Extract top {max_results} teams...")

        tables = page.locator("table.Table")
        table_count = tables.count()
        print(f"  Found {table_count} tables")

        for t in range(0, table_count - 1, 2):
            name_table = tables.nth(t)
            stats_table = tables.nth(t + 1)

            name_rows = name_table.locator("tbody tr")
            stats_rows = stats_table.locator("tbody tr")
            row_count = min(name_rows.count(), stats_rows.count())

            for i in range(row_count):
                if len(results) >= max_results:
                    break
                try:
                    raw = name_rows.nth(i).inner_text(timeout=2000).strip()
                    parts = [p.strip() for p in raw.split("\n") if p.strip()]
                    team_name = parts[-1] if parts else "N/A"

                    stats_text = stats_rows.nth(i).inner_text(timeout=2000).strip()
                    stats = [s.strip() for s in re.split(r"[\t\n]+", stats_text) if s.strip()]
                    wins = stats[0] if len(stats) > 0 else "N/A"
                    losses = stats[1] if len(stats) > 1 else "N/A"

                    if team_name != "N/A":
                        results.append(EspnTeamStanding(
                            team_name=team_name,
                            wins=wins,
                            losses=losses,
                        ))
                        print(f"  {len(results)}. {team_name} | W: {wins} | L: {losses}")
                except Exception as e:
                    print(f"  Error on row {i}: {e}")
                    continue
            if len(results) >= max_results:
                break

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nTop {len(results)} {league} teams:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.team_name}")
            print(f"     Wins: {r.wins}  Losses: {r.losses}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return EspnStandingsResult(
        league=league,
        teams=results,
    )


def test_get_espn_standings() -> None:
    request = EspnStandingsRequest(
        league="NBA",
        max_results=5,
    )

    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=False,
            viewport=None,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = get_espn_standings(page, request)
            assert result.league == request.league
            assert len(result.teams) <= request.max_results
            print(f"\nTotal teams found: {len(result.teams)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_get_espn_standings)
