"""
Auto-generated Playwright script (Python)
Speedrun.com – Game Leaderboard

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class LeaderboardRequest:
    game_slug: str = "sm64"
    game_name: str = "Super Mario 64"
    max_results: int = 5


@dataclass
class RunResult:
    rank: int = 0
    runner: str = ""
    time: str = ""
    date: str = ""
    platform: str = ""


@dataclass
class LeaderboardResult:
    runs: List[RunResult] = field(default_factory=list)


def speedrun_leaderboard(page: Page, request: LeaderboardRequest) -> LeaderboardResult:
    """Extract top speedruns from leaderboard."""
    print(f"  Game: {request.game_name}\n")

    url = f"https://www.speedrun.com/{request.game_slug}"
    print(f"Loading {url}...")
    checkpoint("Navigate to leaderboard")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = LeaderboardResult()

    checkpoint("Extract leaderboard entries")
    js_code = r"""(max) => {
        const body = document.body.innerText;
        const lines = body.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find the second "Verified" (data header vs table header) - entries start after
        let verifiedCount = 0;
        let startIdx = 0;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === 'Verified') {
                verifiedCount++;
                if (verifiedCount === 2) { startIdx = i + 1; break; }
            }
        }
        const timePattern = /^\d+[hms]\s/;
        const runs = [];
        let rank = 1;
        let i = startIdx;
        while (i < lines.length && runs.length < max) {
            let line = lines[i];
            // Skip rank numbers
            if (/^\d+$/.test(line)) { i++; line = lines[i]; }
            // Runner name
            const runner = line;
            i++;
            if (i >= lines.length) break;
            // Time (format: 1h 35m 25s)
            const time = lines[i];
            i++;
            if (i >= lines.length) break;
            // Date (e.g., "8 days ago")
            const date = lines[i];
            i++;
            if (i >= lines.length) break;
            // Platform
            const platform = lines[i];
            i++;
            if (i >= lines.length) break;
            // Verified (Yes/No)
            i++; // skip verified
            if (runner && time && !runner.startsWith('Showing')) {
                runs.push({rank: rank, runner, time, date, platform});
                rank++;
            }
        }
        return runs;
    }"""
    runs_data = page.evaluate(js_code, request.max_results)

    for rd in runs_data:
        run = RunResult()
        run.rank = rd.get("rank", 0)
        run.runner = rd.get("runner", "")
        run.time = rd.get("time", "")
        run.date = rd.get("date", "")
        run.platform = rd.get("platform", "")
        result.runs.append(run)

    for r in result.runs:
        print(f"\n  #{r.rank}: {r.runner}")
        print(f"    Time:     {r.time}")
        print(f"    Date:     {r.date}")
        print(f"    Platform: {r.platform}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("speedrun")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = LeaderboardRequest()
            result = speedrun_leaderboard(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.runs)} runs")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
