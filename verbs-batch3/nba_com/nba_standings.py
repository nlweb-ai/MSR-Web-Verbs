import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


STAT_RE = re.compile(r'^(\d+)\s+(\d+)\s+\.(\d+)\s+(\S+)')


@dataclass(frozen=True)
class NbaStandingsRequest:
    conference: str = "Eastern"
    max_teams: int = 5


@dataclass(frozen=True)
class TeamStanding:
    rank: int
    name: str
    wins: int
    losses: int
    pct: str
    gb: str


@dataclass(frozen=True)
class NbaStandingsResult:
    teams: list  # list[TeamStanding]


# Navigate to the NBA standings page and extract the top N teams
# for the specified conference with team name, wins, losses,
# win percentage, and games behind.
def nba_standings(page: Page, request: NbaStandingsRequest) -> NbaStandingsResult:
    conference = request.conference
    max_teams = request.max_teams
    print(f"  {conference} Conference Top {max_teams} Teams\n")

    results = []

    url = "https://www.nba.com/standings"
    print(f"Loading {url}...")
    checkpoint("Navigate to page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Find the conference section
    conf_header = conference + ' Conference'
    i = 0
    in_conf = False
    while i < len(text_lines) and len(results) < max_teams:
        line = text_lines[i]

        if line == conf_header:
            in_conf = True
            i += 1
            continue

        # Stop at next conference
        if in_conf and 'Conference' in line and line != conf_header and 'TEAM' not in line:
            break

        if in_conf:
            # Look for rank number (1-15)
            if re.match(r'^\d{1,2}$', line):
                rank = int(line)
                # Next lines: city, team_name, marker, stats
                city = text_lines[i + 1] if i + 1 < len(text_lines) else ''
                team = text_lines[i + 2] if i + 2 < len(text_lines) else ''
                # Find stats line (starts with digits: W L)
                for j in range(i + 3, min(i + 6, len(text_lines))):
                    m = STAT_RE.match(text_lines[j])
                    if m:
                        wins = int(m.group(1))
                        losses = int(m.group(2))
                        pct = '.' + m.group(3)
                        gb = m.group(4)
                        full_name = city + ' ' + team
                        results.append(TeamStanding(
                            rank=rank,
                            name=full_name,
                            wins=wins,
                            losses=losses,
                            pct=pct,
                            gb=gb,
                        ))
                        break

        i += 1

    print("=" * 60)
    print(f"NBA {conference} Conference Standings (Top {max_teams})")
    print("=" * 60)
    print(f"{'Team':<28} {'W':>3} {'L':>3} {'PCT':>5} {'GB':>4}")
    print('-' * 48)
    for r in results:
        label = str(r.rank) + '. ' + r.name
        print(f"{label:<28} {r.wins:>3} {r.losses:>3} {r.pct:>5} {r.gb:>4}")

    return NbaStandingsResult(teams=results)


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_user_data = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            chrome_user_data,
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        result = nba_standings(page, NbaStandingsRequest())
        print(f"\nReturned {len(result.teams)} teams")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)