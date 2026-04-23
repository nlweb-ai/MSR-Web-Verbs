"""
Playwright script (Python) — MTGGoldfish Metagame
Browse MTGGoldfish for top Standard format decks.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MTGRequest:
    format: str = "standard"
    max_results: int = 5


@dataclass
class DeckItem:
    name: str = ""
    meta_share: str = ""


@dataclass
class MTGResult:
    decks: List[DeckItem] = field(default_factory=list)


# Browses MTGGoldfish metagame page and extracts top decks
# including deck name, colors, meta share percentage, and price.
def get_mtg_metagame(page: Page, request: MTGRequest) -> MTGResult:
    url = f"https://www.mtggoldfish.com/metagame/{request.format}"
    print(f"Loading {url}...")
    checkpoint("Navigate to MTGGoldfish metagame")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = MTGResult()

    checkpoint("Extract deck listings")
    js_code = """(max) => {
        const results = [];
        const tiles = document.querySelectorAll('.archetype-tile');
        for (const tile of tiles) {
            if (results.length >= max) break;
            const nameEl = tile.querySelector('.deck-price-paper a, h2 a, .archetype-name a, td a');
            const name = nameEl ? nameEl.textContent.trim() : '';
            if (!name || name.length < 2) continue;

            const text = tile.textContent;
            const shareMatch = text.match(/([\\.\\d]+)\\s*%/);
            const meta_share = shareMatch ? shareMatch[0] : '';

            results.push({ name, meta_share });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = DeckItem()
        item.name = d.get("name", "")
        item.meta_share = d.get("meta_share", "")
        result.decks.append(item)

    print(f"\nFound {len(result.decks)} decks:")
    for i, d in enumerate(result.decks, 1):
        print(f"\n  {i}. {d.name}")
        print(f"     Meta: {d.meta_share}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("mtggoldfish")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = get_mtg_metagame(page, MTGRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.decks)} decks")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
