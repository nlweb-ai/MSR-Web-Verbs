import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class NflScheduleRequest:
    team_slug: str = "sea"
    team: str = "Seattle Seahawks"
    max_games: int = 5


@dataclass(frozen=True)
class NflGame:
    week: str
    date: str
    opponent: str
    result: str
    record: str


@dataclass(frozen=True)
class NflScheduleResult:
    team: str
    games: list  # list[NflGame]


RESULT_RE = re.compile(r'^([WLT])(\d+-\d+(?:\s+OT)?)\s+(\d+-\d+(?:-\d+)?)')
WEEK_DATE_RE = re.compile(r'^(\d+|DIV|CONF|SB|WC)\s+(.+)$')


# Navigate to the ESPN schedule page for a given NFL team, parse recent/postseason
# game results (week, date, opponent, result, record), and return up to max_games
# most recent games in chronological order.
def nfl_schedule(page: Page, request: NflScheduleRequest) -> NflScheduleResult:
    print(f"  Team: {request.team}\n")

    url = f"https://www.espn.com/nfl/team/schedule/_/name/{request.team_slug}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to {url}")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Parse game entries
    # Pattern: week+date line -> 'vs'/'@' -> opponent -> result line
    i = 0
    in_schedule = False
    current_section = ""
    post_games = []
    reg_games = []
    while i < len(text_lines):
        line = text_lines[i]

        if line in ('Postseason', 'Regular Season'):
            in_schedule = True
            current_section = line
            i += 2  # skip header row
            continue
        if line == 'Preseason':
            break

        if in_schedule:
            m = WEEK_DATE_RE.match(line)
            if m and line != 'BYE WEEK' and not line.startswith('WK'):
                parts = m.group(0).split(None, 1)
                week = parts[0]
                date = parts[1] if len(parts) > 1 else ''
                # Handle multi-word week (e.g., '8  BYE WEEK')
                if 'BYE' in date:
                    i += 1
                    continue
                home_away = text_lines[i + 1] if i + 1 < len(text_lines) else ''
                opponent = text_lines[i + 2] if i + 2 < len(text_lines) else ''
                result_line = text_lines[i + 3] if i + 3 < len(text_lines) else ''
                rm = RESULT_RE.match(result_line)
                if rm:
                    wl = rm.group(1)
                    score = rm.group(2)
                    record = rm.group(3)
                    prefix = 'vs' if home_away == 'vs' else '@'
                    game = NflGame(
                        week=week,
                        date=date,
                        opponent=f'{prefix} {opponent}',
                        result=f'{wl} {score}',
                        record=record,
                    )
                    if current_section == 'Postseason':
                        post_games.append(game)
                    else:
                        reg_games.append(game)
                    i += 4
                    continue

        i += 1

    # Chronological order: regular season then postseason
    all_games = reg_games + post_games
    # Take last N games (most recent)
    results = all_games[-request.max_games:]

    print("=" * 60)
    print(f"{request.team} - Recent Games")
    print("=" * 60)
    for idx, g in enumerate(results, 1):
        print(f"\n{idx}. Week {g.week}: {g.date}")
        print(f"   Opponent: {g.opponent}")
        print(f"   Result:   {g.result}")
        print(f"   Record:   {g.record}")

    print(f"\nShowing {len(results)} most recent games")

    return NflScheduleResult(team=request.team, games=results)


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
        result = nfl_schedule(page, NflScheduleRequest())
        print(f"\nReturned {len(result.games)} games")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)