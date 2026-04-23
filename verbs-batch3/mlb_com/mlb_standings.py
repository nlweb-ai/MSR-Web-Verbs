import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MlbStandingsRequest:
    league: str = "American League"
    max_teams: int = 5


@dataclass(frozen=True)
class MlbTeamStanding:
    name: str = ""
    wins: int = 0
    losses: int = 0
    gb: str = "-"


@dataclass(frozen=True)
class MlbStandingsResult:
    teams: tuple = ()


AL_TEAMS = {
    "Tampa Bay Rays", "New York Yankees", "Baltimore Orioles", "Toronto Blue Jays", "Boston Red Sox",
    "Minnesota Twins", "Cleveland Guardians", "Detroit Tigers", "Kansas City Royals", "Chicago White Sox",
    "Texas Rangers", "Houston Astros", "Seattle Mariners", "Los Angeles Angels", "Oakland Athletics",
    "Athletics",
}
STAT_RE = re.compile(r'^(\d+)\s+(\d+)\s+\.\d+\s+(\S+)')


# Navigate to mlb.com/standings, scrape the standings table for the requested league,
# and return the top N teams sorted by wins with name, wins, losses, and games behind.
def mlb_standings(page: Page, request: MlbStandingsRequest) -> MlbStandingsResult:
    print(f"  {request.league} Top {request.max_teams} Teams\n")

    url = "https://www.mlb.com/standings"
    print(f"Loading {url}...")
    checkpoint("Navigate to page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    all_teams = []
    i = 0
    while i < len(text_lines) - 1:
        line = text_lines[i]
        if line in AL_TEAMS:
            stat_line = text_lines[i + 1]
            m = STAT_RE.match(stat_line)
            if m:
                wins = int(m.group(1))
                losses = int(m.group(2))
                gb = m.group(3)
                all_teams.append(MlbTeamStanding(name=line, wins=wins, losses=losses, gb=gb))
        i += 1

    # Sort by wins descending, then losses ascending
    all_teams.sort(key=lambda t: (-t.wins, t.losses))
    top = all_teams[:request.max_teams]

    # Recalculate GB from top team
    if top:
        top_w, top_l = top[0].wins, top[0].losses
        recalculated = []
        for t in top:
            diff = ((top_w - t.wins) + (t.losses - top_l)) / 2
            new_gb = "-" if diff == 0 else str(diff)
            recalculated.append(MlbTeamStanding(name=t.name, wins=t.wins, losses=t.losses, gb=new_gb))
        top = recalculated

    print("=" * 60)
    print(f"MLB {request.league} Standings (Top {request.max_teams})")
    print("=" * 60)
    print(f"{'Team':<25} {'W':>3} {'L':>3} {'GB':>5}")
    print("-" * 40)
    for idx, t in enumerate(top, 1):
        label = f"{idx}. {t.name}"
        print(f"{label:<25} {t.wins:>3} {t.losses:>3} {t.gb:>5}")

    print(f"\nTotal teams found: {len(all_teams)}")

    return MlbStandingsResult(teams=tuple(top))


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_profile = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default",
    )
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            chrome_profile,
            headless=False,
            channel="chrome",
        )
        page = context.pages[0] if context.pages else context.new_page()
        request = MlbStandingsRequest()
        result = mlb_standings(page, request)
        print(f"\nReturned {len(result.teams)} teams")
        for t in result.teams:
            print(f"  {t.name}: {t.wins}-{t.losses} (GB {t.gb})")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)