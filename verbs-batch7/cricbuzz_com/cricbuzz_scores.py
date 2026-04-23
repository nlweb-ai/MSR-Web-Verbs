"""
Auto-generated Playwright script (Python)
Cricbuzz – Live Cricket Scores

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
class MatchScoresRequest:
    max_matches: int = 3


@dataclass
class Match:
    team1: str = ""
    team1_score: str = ""
    team2: str = ""
    team2_score: str = ""
    status: str = ""
    venue: str = ""
    match_info: str = ""


@dataclass
class MatchScoresResult:
    matches: List[Match] = field(default_factory=list)


def cricbuzz_scores(page: Page, request: MatchScoresRequest) -> MatchScoresResult:
    """Extract live/recent cricket match scores from Cricbuzz."""
    print(f"  Max matches: {request.max_matches}\n")

    # ── Navigate to live scores page ──────────────────────────────────
    url = "https://www.cricbuzz.com/cricket-match/live-scores"
    print(f"Loading {url}...")
    checkpoint("Navigate to Cricbuzz live scores")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = MatchScoresResult()

    # ── Extract matches via page text parsing ─────────────────────────
    checkpoint("Extract match data")
    js_code = r"""(max) => {
        const text = document.body.innerText;
        // Match blocks start with venue header like "Xth Match • City, Ground"
        const pattern = /(\d+(?:st|nd|rd|th)\s+(?:Match|T20I|ODI|Test|unofficial\s+Test)\s*\u2022\s*[^\n]+)\n([\s\S]*?)(?=\d+(?:st|nd|rd|th)\s+(?:Match|T20I|ODI|Test|unofficial\s+Test)\s*\u2022|FEATURED VIDEOS|LATEST NEWS|$)/g;
        const matches = [];
        let m;
        while ((m = pattern.exec(text)) !== null && matches.length < max) {
            const header = m[1].trim();
            const body = m[2].trim();
            const lines = body.split('\n').map(l => l.trim()).filter(l =>
                l.length > 0 && !['|', 'Live Score', 'Scorecard', 'Full Commentary', 'News'].includes(l)
            );

            // Parse venue from header: "Xth Match • City, Ground"
            const venueParts = header.split('\u2022');
            const matchInfo = venueParts[0].trim();
            const venue = venueParts.length > 1 ? venueParts[1].trim() : '';

            // Parse teams and scores from lines
            let team1 = '', team1Score = '', team2 = '', team2Score = '', status = '';
            const statusPatterns = ['Day', 'won', 'trail', 'lead', 'Stumps', 'Result', 'Match drawn', 'tied', 'innings'];

            let phase = 0; // 0=expecting team1, 1=expecting score1, 2=expecting team2, 3=expecting score2
            for (const line of lines) {
                // Skip series headers (ALL CAPS with year)
                if (line.match(/^[A-Z\s,]+\d{4}$/)) continue;
                // Skip sub-headers
                if (line.match(/\d+(?:st|nd|rd|th)\s+(?:Match|T20I|ODI|Test)/)) continue;

                // Check if this is a status line
                if (statusPatterns.some(p => line.includes(p)) && phase >= 2) {
                    status = line;
                    break;
                }

                // Score lines typically contain digits, /, -, &
                const isScore = /^\d/.test(line) && /[\d\/-]/.test(line) && line.length < 30;

                if (phase === 0) {
                    team1 = line; phase = 1;
                } else if (phase === 1) {
                    if (isScore) { team1Score = line; phase = 2; }
                    else { team1Score = ''; team2 = line; phase = 3; }
                } else if (phase === 2) {
                    team2 = line; phase = 3;
                } else if (phase === 3) {
                    if (isScore) { team2Score = line; phase = 4; }
                    else { status = line; break; }
                }
            }

            matches.push({team1, team1_score: team1Score, team2, team2_score: team2Score, status, venue, match_info: matchInfo});
        }
        return matches;
    }"""
    matches_data = page.evaluate(js_code, request.max_matches)

    for md in matches_data:
        match = Match()
        match.team1 = md.get("team1", "")
        match.team1_score = md.get("team1_score", "")
        match.team2 = md.get("team2", "")
        match.team2_score = md.get("team2_score", "")
        match.status = md.get("status", "")
        match.venue = md.get("venue", "")
        match.match_info = md.get("match_info", "")
        result.matches.append(match)

    # ── Print results ─────────────────────────────────────────────────
    for i, m in enumerate(result.matches, 1):
        print(f"\n  Match {i}:")
        print(f"    Team 1:       {m.team1} ({m.team1_score})")
        print(f"    Team 2:       {m.team2} ({m.team2_score})")
        print(f"    Status:       {m.status}")
        print(f"    Venue:        {m.venue}")
        print(f"    Match Info:   {m.match_info}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("cricbuzz")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = MatchScoresRequest()
            result = cricbuzz_scores(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.matches)} matches")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
