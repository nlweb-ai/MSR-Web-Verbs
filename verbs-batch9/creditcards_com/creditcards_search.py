"""
Playwright script (Python) — CreditCards.com Search
Search for credit cards on CreditCards.com.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CreditCardsSearchRequest:
    category: str = "balance transfer"
    max_results: int = 5


@dataclass
class CreditCardItem:
    name: str = ""
    rating: str = ""
    intro_apr: str = ""
    intro_period: str = ""
    regular_apr: str = ""


@dataclass
class CreditCardsSearchResult:
    category: str = ""
    items: List[CreditCardItem] = field(default_factory=list)


def search_creditcards(page: Page, request: CreditCardsSearchRequest) -> CreditCardsSearchResult:
    """Search CreditCards.com for credit cards."""
    slug = request.category.replace(" ", "-").lower()
    url = f"https://www.creditcards.com/{slug}/"
    print(f"Loading {url}...")
    checkpoint("Navigate to credit cards")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = CreditCardsSearchResult(category=request.category)

    checkpoint("Extract credit cards")
    js_code = """(max) => {
        const items = [];
        const boxes = document.querySelectorAll('[class*="product-box"]');
        // Find top-level product-box containers (not nested)
        for (const box of boxes) {
            if (items.length >= max) break;
            if (box.parentElement.closest('[class*="product-box"]')) continue;
            const lines = box.innerText.split('\\n').map(l => l.trim()).filter(l => l);
            if (lines.length < 10) continue;

            // Line 1 is usually card name (after "BEST FOR..." line)
            let name = '';
            let rating = '';
            let introApr = '';
            let introPeriod = '';
            let regularApr = '';
            for (let j = 0; j < lines.length; j++) {
                const line = lines[j];
                if (!name && j < 5 && !line.startsWith('BEST') && !line.startsWith('Our')
                    && line.length > 5 && /[A-Z]/.test(line[0])) {
                    name = line;
                }
                if (line === 'Our rating:' && j + 1 < lines.length) {
                    rating = lines[j + 1];
                }
                if (line === 'Intro balance transfer APR' && j + 1 < lines.length) {
                    introApr = lines[j + 1];
                }
                if (line === 'Intro balance transfer period' && j + 1 < lines.length) {
                    introPeriod = lines[j + 1];
                }
                if (line === 'Regular balance transfer APR' && j + 1 < lines.length) {
                    regularApr = lines[j + 1];
                }
            }
            if (!name) continue;
            if (items.some(i => i.name === name)) continue;
            items.push({name, rating, intro_apr: introApr, intro_period: introPeriod, regular_apr: regularApr});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = CreditCardItem()
        item.name = d.get("name", "")
        item.rating = d.get("rating", "")
        item.intro_apr = d.get("intro_apr", "")
        item.intro_period = d.get("intro_period", "")
        item.regular_apr = d.get("regular_apr", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} credit cards in '{request.category}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name}  (Rating: {item.rating})")
        print(f"     Intro APR: {item.intro_apr}")
        print(f"     Intro Period: {item.intro_period}")
        print(f"     Regular APR: {item.regular_apr}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("creditcards")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_creditcards(page, CreditCardsSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} cards")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
