"""Playwright script (Python) — WhoScored"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class WhoScoredRequest:
    max_results: int = 10

@dataclass
class PlayerItem:
    name: str = ""
    team: str = ""
    age: str = ""
    position: str = ""
    rating: str = ""

@dataclass
class WhoScoredResult:
    players: List[PlayerItem] = field(default_factory=list)

def get_whoscored_rankings(page: Page, request: WhoScoredRequest) -> WhoScoredResult:
    url = "https://www.whoscored.com/Statistics"
    checkpoint("Navigate to WhoScored statistics")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = WhoScoredResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find player section: pattern is Number → Name → "Team, Age, Position" → Stats line
        let inPlayers = false;
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'Player Statistics') inPlayers = true;
            if (!inPlayers) continue;
            // Number line (just digits)
            if (/^\\d+$/.test(lines[i]) && i + 2 < lines.length) {
                const name = lines[i + 1];
                const infoLine = lines[i + 2]; // "Team, Age, Position"
                const statsLine = (i + 3 < lines.length) ? lines[i + 3] : '';
                if (!name || name.length < 3) continue;
                // Parse info: "Barcelona, 18, AM(R)"
                const parts = infoLine.split(',').map(s => s.trim());
                const team = parts[0] || '';
                const age = parts[1] || '';
                const position = parts.slice(2).join(', ') || '';
                // Rating is last number in stats line
                const statParts = statsLine.split(/\\s+/);
                const rating = statParts.length > 0 ? statParts[statParts.length - 1] : '';
                results.push({ name, team, age, position, rating });
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = PlayerItem()
        item.name = d.get("name", "")
        item.team = d.get("team", "")
        item.age = d.get("age", "")
        item.position = d.get("position", "")
        item.rating = d.get("rating", "")
        result.players.append(item)

    print(f"\nFound {len(result.players)} players:")
    for i, p in enumerate(result.players, 1):
        print(f"  {i}. {p.name} ({p.team}, {p.age}, {p.position}) - Rating: {p.rating}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("whoscored")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            get_whoscored_rankings(page, WhoScoredRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
