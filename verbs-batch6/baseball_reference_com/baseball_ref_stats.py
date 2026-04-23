"""
Auto-generated Playwright script (Python)
Baseball Reference – Player Stats
Player: "Shohei Ohtani"

Generated on: 2026-04-18T04:54:12.306Z
Recorded 2 browser interactions
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
    player: str = "Shohei Ohtani"


@dataclass
class PlayerStats:
    player_name: str = ""
    batting_avg: str = ""
    home_runs: str = ""
    rbis: str = ""
    hits: str = ""
    games_played: str = ""


def baseball_ref_search(page: Page, request: PlayerRequest) -> PlayerStats:
    """Search Baseball Reference for player stats."""
    print(f"  Player: {request.player}\n")

    url = f"https://www.baseball-reference.com/search/search.fcgi?search={quote_plus(request.player)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Baseball Reference search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # May auto-redirect to player page, or need to click first result
    current_url = page.url
    if "/search/" in current_url:
        try:
            first_link = page.locator('.search-item-name a, .search-results a').first
            if first_link.is_visible(timeout=3000):
                first_link.click()
                page.wait_for_timeout(5000)
        except Exception:
            pass

    checkpoint("Extract batting stats")
    body_text = page.evaluate("document.body.innerText") or ""

    player_name = request.player
    batting_avg = ""
    home_runs = ""
    rbis = ""
    hits = ""
    games_played = ""

    # Player name
    try:
        h1 = page.locator("h1").first
        if h1.is_visible(timeout=2000):
            player_name = h1.inner_text().strip()
    except Exception:
        pass

    # Look for career totals in batting table
    bam = re.search(r"(?:Career|Total).*?(\.\d{3}).*?(\d+)\s+HR", body_text, re.IGNORECASE | re.DOTALL)
    if bam:
        batting_avg = bam.group(1)

    # Individual stats from body text
    hrm = re.search(r"(\d+)\s+(?:HR|Home Runs?)", body_text, re.IGNORECASE)
    if hrm:
        home_runs = hrm.group(1)

    rbim = re.search(r"(\d+)\s+(?:RBI|Runs? Batted In)", body_text, re.IGNORECASE)
    if rbim:
        rbis = rbim.group(1)

    htm = re.search(r"(\d+)\s+(?:H\b|Hits?)", body_text, re.IGNORECASE)
    if htm:
        hits = htm.group(1)

    gm = re.search(r"(\d+)\s+(?:G\b|Games?)", body_text, re.IGNORECASE)
    if gm:
        games_played = gm.group(1)

    result = PlayerStats(
        player_name=player_name,
        batting_avg=batting_avg,
        home_runs=home_runs,
        rbis=rbis,
        hits=hits,
        games_played=games_played,
    )

    print("\n" + "=" * 60)
    print(f"Baseball Reference: {result.player_name}")
    print("=" * 60)
    print(f"  Batting Avg:  {result.batting_avg}")
    print(f"  Home Runs:    {result.home_runs}")
    print(f"  RBIs:         {result.rbis}")
    print(f"  Hits:         {result.hits}")
    print(f"  Games Played: {result.games_played}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("baseball_ref")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = baseball_ref_search(page, PlayerRequest())
            print(f"\nReturned stats for {result.player_name}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
