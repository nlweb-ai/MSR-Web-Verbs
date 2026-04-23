"""
Auto-generated Playwright script (Python)
GOG – Game Search
Query: "roguelike"

Generated on: 2026-04-18T05:27:39.587Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GameRequest:
    query: str = "roguelike"
    max_results: int = 5


@dataclass
class Game:
    title: str = ""
    price: str = ""
    discount: str = ""
    rating: str = ""
    url: str = ""


@dataclass
class GameResult:
    games: list = field(default_factory=list)


def gog_search(page: Page, request: GameRequest) -> GameResult:
    """Search GOG for games."""
    print(f"  Query: {request.query}\n")

    # ── Step 1: Navigate to GOG search ────────────────────────────────
    url = f"https://www.gog.com/en/games?query={quote_plus(request.query)}"
    print(f"Loading GOG search...")
    checkpoint("Navigate to GOG search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Step 2: Extract game tiles ────────────────────────────────────
    checkpoint("Extract game listings")
    items = page.evaluate(r"""(maxResults) => {
        const tiles = document.querySelectorAll('.product-tile');
        const results = [];
        for (const tile of tiles) {
            if (results.length >= maxResults) break;
            const titleEl = tile.querySelector('[selenium-id="productTitle"]');
            const title = titleEl ? titleEl.innerText.trim() : '';
            if (!title) continue;

            // Skip DLCs
            const labelEl = tile.querySelector('[selenium-id="productTitleLabel"]');
            if (labelEl && /^DLC$/i.test(labelEl.innerText.trim())) continue;

            // Skip "Coming soon"
            const priceEl = tile.querySelector('[selenium-id="productPrice"]');
            if (priceEl && /coming soon/i.test(priceEl.innerText)) continue;

            const discountEl = tile.querySelector('[selenium-id="productPriceDiscount"]');
            const discount = discountEl ? discountEl.innerText.trim() : '';

            const valueEl = tile.querySelector('[selenium-id="productPriceValue"]');
            let price = valueEl ? valueEl.innerText.trim() : '';
            // For discounted items, price text is "original\ndiscounted" — take last line
            if (price.includes('\n')) {
                const parts = price.split('\n').map(p => p.trim()).filter(Boolean);
                price = parts[parts.length - 1];
            }

            const url = tile.href || '';

            results.push({ title, price, discount, url });
        }
        return results;
    }""", request.max_results)

    result = GameResult(games=[Game(
        title=g['title'], price=g['price'], discount=g['discount'], url=g['url']
    ) for g in items])

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"GOG: \"{request.query}\"")
    print("=" * 60)
    for g in items:
        disc = f"  ({g['discount']})" if g['discount'] else ""
        print(f"\n  {g['title']}")
        print(f"    Price: {g['price']}{disc}")
        print(f"    URL: {g['url']}")
    print(f"\n  Total: {len(items)} games")
    if not any(g.get('rating') for g in items):
        print("  Note: Ratings not shown on GOG search results page")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("gog_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = gog_search(page, GameRequest())
            print(f"\nReturned {len(result.games)} games")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
