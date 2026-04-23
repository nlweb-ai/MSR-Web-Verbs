"""
Playwright script (Python) — Lichess Puzzle Themes
Browse Lichess puzzle themes and extract theme details.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class LichessRequest:
    max_results: int = 5


@dataclass
class PuzzleTheme:
    theme: str = ""
    count: str = ""


@dataclass
class LichessResult:
    themes: List[PuzzleTheme] = field(default_factory=list)


# Browses Lichess puzzle themes page and extracts theme names and puzzle counts.
def browse_lichess_puzzles(page: Page, request: LichessRequest) -> LichessResult:
    url = "https://lichess.org/training/themes"
    print(f"Loading {url}...")
    checkpoint("Navigate to Lichess puzzle themes")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = LichessResult()

    checkpoint("Extract puzzle themes")
    js_code = """(max) => {
        const results = [];
        // Get page text and find theme entries (name + count + description pattern)
        const body = document.body.innerText;
        // Match patterns like "Healthy mix6,228,283" or "Opening315,006"
        const regex = /^(.+?)([\\d,]{3,})$/gm;
        let match;
        while ((match = regex.exec(body)) !== null && results.length < max) {
            const theme = match[1].trim();
            const count = match[2].trim();
            if (!theme || theme.length < 2) continue;
            // Skip nav items
            if (/^(Puzzle|Play|Sign|Log|Learn|Watch|Community|Tools|PLAY|PUZZLES|LEARN|WATCH|SIGN|REGISTER|DONATE)/.test(theme)) continue;
            results.push({ theme, count });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = PuzzleTheme()
        item.theme = d.get("theme", "")
        item.count = d.get("count", "")
        result.themes.append(item)

    print(f"\nFound {len(result.themes)} puzzle themes:")
    for i, item in enumerate(result.themes, 1):
        print(f"\n  {i}. {item.theme}")
        print(f"     Count: {item.count}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("lichess")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = browse_lichess_puzzles(page, LichessRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.themes)} puzzle themes")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
