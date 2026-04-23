"""
Playwright script (Python) — Chess.com Leaderboard
Browse chess leaderboard on Chess.com.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ChessLeaderboardRequest:
    category: str = "blitz"
    max_results: int = 10


@dataclass
class PlayerItem:
    rank: str = ""
    username: str = ""
    rating: str = ""
    title: str = ""
    won: str = ""
    draw: str = ""
    lost: str = ""


@dataclass
class ChessLeaderboardResult:
    category: str = ""
    items: List[PlayerItem] = field(default_factory=list)


def get_chess_leaderboard(page: Page, request: ChessLeaderboardRequest) -> ChessLeaderboardResult:
    """Get Chess.com leaderboard for a category."""
    url = f"https://www.chess.com/leaderboard/live/{request.category}"
    print(f"Loading {url}...")
    checkpoint("Navigate to leaderboard")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = ChessLeaderboardResult(category=request.category)

    checkpoint("Extract leaderboard")
    js_code = """(max) => {
        const items = [];
        const rows = document.querySelectorAll('tr');
        for (const row of rows) {
            if (items.length >= max) break;
            const cells = row.querySelectorAll('td');
            if (cells.length < 7) continue;

            const rankText = cells[1].innerText.trim().replace('#', '');
            if (!rankText || !/^\\d+$/.test(rankText)) continue;

            // Cell 2 has title and username on separate lines
            const playerLines = cells[2].innerText.trim().split('\\n').filter(l => l.trim());
            let title = '';
            let username = '';
            if (playerLines.length >= 2) {
                title = playerLines[0].trim();
                username = playerLines[1].trim();
            } else if (playerLines.length === 1) {
                username = playerLines[0].trim();
            }
            if (!username) continue;
            if (items.some(i => i.username === username)) continue;

            const rating = cells[3].innerText.trim();
            const won = cells[4].innerText.trim();
            const draw = cells[5].innerText.trim();
            const lost = cells[6].innerText.trim();

            items.push({rank: rankText, username, rating, title, won, draw, lost});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = PlayerItem()
        item.rank = d.get("rank", "")
        item.username = d.get("username", "")
        item.rating = d.get("rating", "")
        item.title = d.get("title", "")
        item.won = d.get("won", "")
        item.draw = d.get("draw", "")
        item.lost = d.get("lost", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} players in '{request.category}' leaderboard:")
    for i, item in enumerate(result.items, 1):
        print(f"  {item.rank}. {item.title} {item.username} — Rating: {item.rating}  W/D/L: {item.won}/{item.draw}/{item.lost}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("chess")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = get_chess_leaderboard(page, ChessLeaderboardRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} players")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
