import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class NhlStandingsRequest:
    conference: str = "Eastern"
    max_teams: int = 10

@dataclass(frozen=True)
class NhlTeamStanding:
    team_name: str
    wins: int
    losses: int
    ot_losses: int
    points: int

@dataclass(frozen=True)
class NhlStandingsResult:
    conference: str
    teams: list  # list[NhlTeamStanding]

# Navigate to the NHL standings page and extract standings for the specified
# conference with team name, wins, losses, OT losses, and points for up to
# max_teams teams.
def nhl_standings(page: Page, request: NhlStandingsRequest) -> NhlStandingsResult:
    conference = request.conference
    max_teams = request.max_teams
    print(f"  {conference} Conference Top {max_teams} Teams\n")

    results = []

    url = "https://www.nhl.com/standings"
    print(f"Loading {url}...")
    checkpoint("Navigate to NHL standings")
    page.goto(url, wait_until="domcontentloaded")

    # Wait for the standings tables to render
    try:
        page.wait_for_selector("table", timeout=20000)
    except Exception:
        pass

    # NHL standings page has 6 tables:
    # Eastern: 0=Atlantic, 1=Metropolitan, 2=Wild Card
    # Western: 3=Central, 4=Pacific, 5=Wild Card
    conf_tables = {"Eastern": [0, 1, 2], "Western": [3, 4, 5]}
    table_indices = conf_tables.get(conference, [0, 1, 2])

    tables = page.locator("table")
    table_count = tables.count()
    print(f"  Found {table_count} tables")

    for tidx in table_indices:
        if tidx >= table_count or len(results) >= max_teams:
            break
        try:
            text = tables.nth(tidx).inner_text(timeout=5000)
        except Exception:
            continue

        lines = [l.strip() for l in text.split("\n") if l.strip()]

        # Skip header row (Rank, Team, GP, W, L, OT, PTS, ...)
        # Data rows: rank(number), team_name, clinch_letter?, GP, W, L, OT, PTS, ...
        i = 0
        # Skip past headers
        while i < len(lines) and not re.match(r"^\d+$", lines[i]):
            i += 1

        while i < len(lines) and len(results) < max_teams:
            # Expect: rank number
            if not re.match(r"^\d+$", lines[i]):
                i += 1
                continue

            i += 1  # skip rank

            if i >= len(lines):
                break
            team_name = lines[i]
            i += 1

            if i >= len(lines):
                break
            # Next line could be a clinch indicator (Y, X, Z, E, P) or GP number
            if re.match(r"^[A-Z]{1,2}$", lines[i]) and not re.match(r"^\d{2,}$", lines[i]):
                i += 1  # skip clinch indicator

            # Now expect: GP, W, L, OT, PTS, ...
            if i + 4 >= len(lines):
                break
            try:
                gp = int(lines[i])
                wins = int(lines[i + 1])
                losses = int(lines[i + 2])
                ot_losses = int(lines[i + 3])
                points = int(lines[i + 4])
            except (ValueError, IndexError):
                i += 1
                continue

            results.append(NhlTeamStanding(
                team_name=team_name,
                wins=wins,
                losses=losses,
                ot_losses=ot_losses,
                points=points,
            ))

            # Skip remaining columns in this row to get to next rank
            # Remaining: P%, RW, ROW, GF, GA, DIFF, HOME, AWAY, S/O, L10, STRK
            i += 5
            while i < len(lines) and not re.match(r"^\d+$", lines[i]):
                i += 1

    print("=" * 60)
    print(f"NHL {conference} Conference Standings (Top {max_teams})")
    print("=" * 60)
    print(f"{'Team':<30} {'W':>3} {'L':>3} {'OTL':>4} {'PTS':>4}")
    print('-' * 48)
    for idx, t in enumerate(results, 1):
        label = str(idx) + '. ' + t.team_name
        print(f"{label:<30} {t.wins:>3} {t.losses:>3} {t.ot_losses:>4} {t.points:>4}")

    return NhlStandingsResult(conference=conference, teams=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = nhl_standings(page, NhlStandingsRequest())
        print(f"\nReturned {len(result.teams)} teams")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
