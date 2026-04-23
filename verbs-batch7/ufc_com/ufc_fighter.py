"""
Auto-generated Playwright script (Python)
UFC – Fighter Profile

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
class FighterRequest:
    fighter_slug: str = "jon-jones"


@dataclass
class FightResult:
    opponent: str = ""
    date: str = ""
    result: str = ""
    method: str = ""
    round: str = ""


@dataclass
class FighterProfile:
    name: str = ""
    nickname: str = ""
    record: str = ""
    weight_class: str = ""
    height: str = ""
    reach: str = ""
    recent_fights: List[FightResult] = field(default_factory=list)


def ufc_fighter(page: Page, request: FighterRequest) -> FighterProfile:
    """Get UFC fighter profile."""
    print(f"  Fighter: {request.fighter_slug}\n")

    url = f"https://www.ufc.com/athlete/{request.fighter_slug}"
    print(f"Loading {url}...")
    checkpoint("Navigate to fighter page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    profile = FighterProfile()

    checkpoint("Extract fighter info")
    js_code = r"""() => {
        const lines = document.body.innerText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        let name = '', nickname = '', record = '', weight_class = '';
        // Find name (ALL CAPS after nickname in quotes)
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].startsWith('"') && lines[i].endsWith('"')) {
                nickname = lines[i].replace(/"/g, '');
                if (i + 1 < lines.length) name = lines[i + 1];
                // Weight class is before "Active"/"Inactive" status, which is before nickname
                for (let j = i - 1; j >= 0; j--) {
                    if (lines[j].includes('Division')) { weight_class = lines[j]; break; }
                }
                break;
            }
        }
        // Find record (W-L-D pattern)
        for (let i = 0; i < lines.length; i++) {
            if (/^\d+-\d+-\d+\s*\(W-L-D\)$/.test(lines[i])) {
                record = lines[i]; break;
            }
        }
        // Find height and reach from INFO section
        let height = '', reach = '';
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === 'HEIGHT' && i + 1 < lines.length) height = lines[i + 1];
            if (lines[i] === 'REACH' && i + 1 < lines.length) reach = lines[i + 1];
        }
        // Find recent fights from ATHLETE RECORD section
        const fights = [];
        let inRecord = false;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === 'ATHLETE RECORD') { inRecord = true; continue; }
            if (!inRecord) continue;
            if (lines[i] === 'LOAD MORE' || lines[i] === 'INFO') break;
            if ((lines[i] === 'WIN' || lines[i] === 'LOSS' || lines[i] === 'DRAW') && fights.length < 3) {
                const result = lines[i];
                const matchup = lines[i + 1] || '';
                const date = lines[i + 2] || '';
                let round = '', method = '';
                // Look for Round and Method
                for (let j = i + 3; j < Math.min(i + 10, lines.length); j++) {
                    if (lines[j] === 'Round' && j + 1 < lines.length) round = lines[j + 1];
                    if (lines[j] === 'Method' && j + 1 < lines.length) method = lines[j + 1];
                    if (lines[j] === 'WATCH REPLAY' || lines[j] === 'FIGHT CARD') break;
                }
                fights.push({opponent: matchup, date, result, method, round});
            }
        }
        return {name, nickname, record, weight_class, height, reach, fights};
    }"""
    data = page.evaluate(js_code)

    profile.name = data.get("name", "")
    profile.nickname = data.get("nickname", "")
    profile.record = data.get("record", "")
    profile.weight_class = data.get("weight_class", "")
    profile.height = data.get("height", "")
    profile.reach = data.get("reach", "")

    for fd in data.get("fights", []):
        f = FightResult()
        f.opponent = fd.get("opponent", "")
        f.date = fd.get("date", "")
        f.result = fd.get("result", "")
        f.method = fd.get("method", "")
        f.round = fd.get("round", "")
        profile.recent_fights.append(f)

    print(f"  Name:         {profile.name}")
    print(f"  Nickname:     {profile.nickname}")
    print(f"  Record:       {profile.record}")
    print(f"  Weight Class: {profile.weight_class}")
    print(f"  Height:       {profile.height}")
    print(f"  Reach:        {profile.reach}")
    print(f"\n  Recent Fights:")
    for i, f in enumerate(profile.recent_fights, 1):
        print(f"    {i}. {f.result} - {f.opponent} ({f.date}) R{f.round} by {f.method}")

    return profile


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("ufc")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = FighterRequest()
            result = ufc_fighter(page, request)
            print("\n=== DONE ===")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
