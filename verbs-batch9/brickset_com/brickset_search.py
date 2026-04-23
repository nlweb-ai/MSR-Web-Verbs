"""
Playwright script (Python) — Brickset Search
Search for LEGO sets on Brickset by theme.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BricksetSearchRequest:
    theme: str = "Star Wars"
    max_results: int = 5


@dataclass
class LegoSetItem:
    name: str = ""
    set_number: str = ""
    piece_count: str = ""
    price: str = ""
    year_released: str = ""
    rating: str = ""


@dataclass
class BricksetSearchResult:
    theme: str = ""
    items: List[LegoSetItem] = field(default_factory=list)


def search_brickset(page: Page, request: BricksetSearchRequest) -> BricksetSearchResult:
    """Search Brickset for LEGO sets by theme."""
    theme_slug = request.theme.replace(" ", "-")
    url = f"https://brickset.com/sets/theme-{theme_slug}"
    print(f"Loading {url}...")
    checkpoint("Navigate to theme page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = BricksetSearchResult(theme=request.theme)

    checkpoint("Extract LEGO sets")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('article.set');
        for (const card of cards) {
            if (items.length >= max) break;
            const lines = card.innerText.split('\\n').map(l => l.trim()).filter(l => l);
            if (lines.length < 3) continue;

            // First line: "3219: Mini TIE Fighter"
            const titleMatch = lines[0].match(/^(\\d+):\\s*(.+)/);
            if (!titleMatch) continue;
            const setNumber = titleMatch[1];
            const name = titleMatch[2];
            if (items.some(i => i.name === name)) continue;

            // Rating from star line: "3.3 87 RATINGS"
            let rating = '';
            for (const line of lines) {
                const rm = line.match(/(\\d\\.\\d)\\s+\\d+\\s+RATINGS/);
                if (rm) { rating = rm[1]; break; }
            }

            // Pieces: line after "PIECES"
            let pieces = '';
            for (let i = 0; i < lines.length; i++) {
                if (lines[i] === 'PIECES' && i + 1 < lines.length) {
                    const pm = lines[i+1].match(/^(\\d[\\d,]*)$/);
                    if (pm) pieces = pm[1];
                    break;
                }
            }

            // Price: line after "RRP" (retail price)
            let price = '';
            for (let i = 0; i < lines.length; i++) {
                if (lines[i] === 'RRP' && i + 1 < lines.length) {
                    const pm = lines[i+1].match(/^(\\$[\\d,.]+|\\xa3[\\d,.]+|\\u20ac[\\d,.]+)$/);
                    if (pm) price = pm[1];
                    break;
                }
            }
            // Fallback: VALUE NEW
            if (!price) {
                for (let i = 0; i < lines.length; i++) {
                    if (lines[i] === 'VALUE NEW' && i + 1 < lines.length) {
                        const pm = lines[i+1].match(/^~?(\\$[\\d,.]+)/);
                        if (pm) { price = '~' + pm[1]; break; }
                    }
                }
            }

            // Year from second line: "3219-1 STAR WARS MINI BUILDING SET 2003"
            let year = '';
            if (lines.length > 1) {
                const ym = lines[1].match(/(20[0-2]\\d|199\\d)/);
                if (ym) year = ym[1];
            }

            items.push({name: name, set_number: setNumber, piece_count: pieces, price: price, year_released: year, rating: rating});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = LegoSetItem()
        item.name = d.get("name", "")
        item.set_number = d.get("set_number", "")
        item.piece_count = d.get("piece_count", "")
        item.price = d.get("price", "")
        item.year_released = d.get("year_released", "")
        item.rating = d.get("rating", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} LEGO sets for '{request.theme}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name} (#{item.set_number})")
        print(f"     Pieces: {item.piece_count}  Price: {item.price}  Year: {item.year_released}  Rating: {item.rating}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("brickset")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_brickset(page, BricksetSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} sets")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
