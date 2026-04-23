"""
Playwright script (Python) — NerdWallet Travel Credit Cards
Browse NerdWallet for best travel credit cards.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class NerdWalletRequest:
    max_results: int = 5


@dataclass
class CardItem:
    name: str = ""
    annual_fee: str = ""
    rating: str = ""
    best_for: str = ""


@dataclass
class NerdWalletResult:
    cards: List[CardItem] = field(default_factory=list)


# Browses NerdWallet travel credit cards and extracts card name,
# issuer, annual fee, rewards rate, sign-up bonus, and rating.
def get_nerdwallet_cards(page: Page, request: NerdWalletRequest) -> NerdWalletResult:
    url = "https://www.nerdwallet.com/best/credit-cards/travel"
    print(f"Loading {url}...")
    checkpoint("Navigate to NerdWallet travel cards")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = NerdWalletResult()

    checkpoint("Extract credit card listings")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        const lines = document.body.innerText.split('\\n').map(l => l.trim()).filter(l => l);
        const h3s = document.querySelectorAll('h3');
        for (const h3 of h3s) {
            if (results.length >= max) break;
            const name = h3.innerText.trim();
            if (!name || name.length < 5 || seen.has(name)) continue;
            // Find this name in body lines
            const idx = lines.findIndex(l => l === name);
            if (idx < 0) continue;
            // Pattern: Name -> Rating -> "Best for..." -> $fee
            const rating = (idx + 1 < lines.length && lines[idx + 1].match(/\\d\\.\\d\\/5/)) ? lines[idx + 1] : '';
            const bestForLine = (idx + 2 < lines.length && lines[idx + 2].startsWith('Best for')) ? lines[idx + 2] : '';
            const best_for = bestForLine.replace(/^Best for\\s+/, '');
            const feeLine = (idx + 3 < lines.length && lines[idx + 3].startsWith('$')) ? lines[idx + 3] : '';
            if (!rating && !feeLine) continue;
            seen.add(name);
            results.push({ name, annual_fee: feeLine, rating, best_for });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = CardItem()
        item.name = d.get("name", "")
        item.annual_fee = d.get("annual_fee", "")
        item.rating = d.get("rating", "")
        item.best_for = d.get("best_for", "")
        result.cards.append(item)

    print(f"\nFound {len(result.cards)} cards:")
    for i, c in enumerate(result.cards, 1):
        print(f"\n  {i}. {c.name}")
        print(f"     Annual Fee: {c.annual_fee}  Rating: {c.rating}  Best for: {c.best_for}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("nerdwallet")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = get_nerdwallet_cards(page, NerdWalletRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.cards)} cards")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
