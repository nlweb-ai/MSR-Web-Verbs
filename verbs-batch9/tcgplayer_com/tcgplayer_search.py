"""Playwright script (Python) — TCGPlayer"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class TCGPlayerRequest:
    query: str = "Charizard"
    max_results: int = 5

@dataclass
class CardItem:
    name: str = ""
    set_name: str = ""
    rarity: str = ""
    price: str = ""
    market_price: str = ""

@dataclass
class TCGPlayerResult:
    cards: List[CardItem] = field(default_factory=list)

def search_tcgplayer(page: Page, request: TCGPlayerRequest) -> TCGPlayerResult:
    url = f"https://www.tcgplayer.com/search/pokemon/product?q={request.query.replace(' ', '+')}"
    checkpoint("Navigate to TCGPlayer search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = TCGPlayerResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: "X listings from" followed by price then "Market Price:$X"
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (/^\\d+ listings? from$/.test(lines[i]) && i >= 1) {
                // Card name is just above
                const name = lines[i - 1];
                // Check for rarity line above name (contains #)
                let rarity = '';
                let set_name = '';
                if (i >= 2 && lines[i - 2].includes('#')) {
                    rarity = lines[i - 2];
                    set_name = (i >= 3) ? lines[i - 3] : '';
                } else {
                    set_name = (i >= 2) ? lines[i - 2] : '';
                }
                // Price on next line
                const price = (i + 1 < lines.length && lines[i + 1].startsWith('$')) ? lines[i + 1] : '';
                // Market price
                const mpLine = (i + 2 < lines.length && lines[i + 2].startsWith('Market Price:')) ? lines[i + 2] : '';
                const market_price = mpLine.replace('Market Price:', '');
                if (name && !name.includes('listings')) {
                    results.push({ name, set_name, rarity, price, market_price });
                }
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = CardItem()
        item.name = d.get("name", "")
        item.set_name = d.get("set_name", "")
        item.rarity = d.get("rarity", "")
        item.price = d.get("price", "")
        item.market_price = d.get("market_price", "")
        result.cards.append(item)

    print(f"\nFound {len(result.cards)} cards:")
    for i, c in enumerate(result.cards, 1):
        print(f"  {i}. {c.name} [{c.set_name}] {c.rarity} - {c.price} (mkt: {c.market_price})")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("tcgplayer")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_tcgplayer(page, TCGPlayerRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
