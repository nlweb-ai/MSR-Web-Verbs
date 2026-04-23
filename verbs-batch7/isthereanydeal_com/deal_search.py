"""
Auto-generated Playwright script (Python)
IsThereAnyDeal – Search game deals

Uses CDP-launched Chrome to avoid bot detection.
Two-step: search → navigate to detail page → extract pricing info.
"""

import os, sys, shutil, re, urllib.parse
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class DealSearchRequest:
    query: str = "Baldur's Gate 3"


@dataclass
class StorePrice:
    store: str = ""
    store_low: str = ""
    current_price: str = ""
    regular_price: str = ""


@dataclass
class DealSearchResult:
    game_name: str = ""
    current_best_price: str = ""
    current_best_store: str = ""
    all_time_low: str = ""
    all_time_low_store: str = ""
    store_prices: List[StorePrice] = field(default_factory=list)


def deal_search(page: Page, request: DealSearchRequest) -> DealSearchResult:
    """Search IsThereAnyDeal for a game and extract pricing info."""
    print(f"  Query: {request.query}\n")

    checkpoint("Search for game on ITAD")
    q = urllib.parse.quote_plus(request.query)
    page.goto(
        f"https://isthereanydeal.com/search/?q={q}",
        wait_until="domcontentloaded",
    )
    page.wait_for_timeout(5000)

    checkpoint("Click first game result to go to detail page")
    detail_url = page.evaluate(r"""() => {
        const link = document.querySelector('a[href*="/game/"][href*="/info/"]');
        return link ? link.href : null;
    }""")

    if not detail_url:
        print("  No game found in search results")
        return DealSearchResult()

    page.goto(detail_url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract pricing information")
    result = DealSearchResult()

    info = page.evaluate(r"""() => {
        const body = document.body.innerText;

        // Game name from h1 or page title
        const h1 = document.querySelector('h1');
        const gameName = h1 ? h1.textContent.trim() : '';

        // Current best price + store
        const bestMatch = body.match(/Current best\s*\n?\s*\$?([\d.]+)\s*\n?\s*(\w[\w\s]*?)(?:\n|$)/);
        const currentBestPrice = bestMatch ? '$' + bestMatch[1] : '';
        const currentBestStore = bestMatch ? bestMatch[2].trim() : '';

        // All time low - parse from structured lines
        const lines = body.split('\n').map(l => l.trim()).filter(Boolean);
        let allTimeLow = '', allTimeLowStore = '';
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === 'All time low') {
                // Next lines: date, store, discount, price
                for (let j = i + 1; j < Math.min(i + 6, lines.length); j++) {
                    if (lines[j].match(/^(Steam|GOG|Epic Game Store|Humble Store)/)) {
                        allTimeLowStore = lines[j];
                    }
                    if (lines[j].match(/^\$[\d.]+$/)) {
                        allTimeLow = lines[j];
                        break;
                    }
                }
                break;
            }
        }

        // Store prices table
        const storePrices = [];
        // Look for rows in the prices table
        const rows = body.match(/^(Steam|GOG|Epic Game Store|Humble Store)\s*\n?.*?\$([\d.]+).*?\$([\d.]+).*?\$([\d.]+)/gm);
        
        return {
            game_name: gameName,
            current_best_price: currentBestPrice,
            current_best_store: currentBestStore,
            all_time_low: allTimeLow,
            all_time_low_store: allTimeLowStore,
        };
    }""")

    result.game_name = info.get("game_name", "")
    result.current_best_price = info.get("current_best_price", "")
    result.current_best_store = info.get("current_best_store", "")
    result.all_time_low = info.get("all_time_low", "")
    result.all_time_low_store = info.get("all_time_low_store", "")

    # Extract store prices from table
    store_data = page.evaluate(r"""() => {
        const rows = document.querySelectorAll('table tr, [class*="price-row"]');
        const stores = [];
        // Try extracting from innerText lines
        const lines = document.body.innerText.split('\n').map(l => l.trim()).filter(Boolean);
        let inPrices = false;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === 'Prices') { inPrices = true; continue; }
            if (inPrices && (lines[i] === 'Steam' || lines[i] === 'GOG' || lines[i] === 'Epic Game Store')) {
                const store = lines[i];
                // Look ahead for price values
                const priceLines = [];
                for (let j = i + 1; j < Math.min(i + 8, lines.length); j++) {
                    if (lines[j].match(/^\$[\d.]+$/)) priceLines.push(lines[j]);
                    if (lines[j] === 'Steam' || lines[j] === 'GOG' || lines[j] === 'Epic Game Store' || lines[j] === 'DLCs') break;
                }
                if (priceLines.length >= 2) {
                    stores.push({
                        store: store,
                        store_low: priceLines[0],
                        current_price: priceLines.length >= 3 ? priceLines[2] : priceLines[1],
                        regular_price: priceLines.length >= 3 ? priceLines[2] : priceLines[1]
                    });
                }
            }
        }
        return stores;
    }""")

    for sp in store_data:
        s = StorePrice()
        s.store = sp.get("store", "")
        s.store_low = sp.get("store_low", "")
        s.current_price = sp.get("current_price", "")
        s.regular_price = sp.get("regular_price", "")
        result.store_prices.append(s)

    print(f"  Game:             {result.game_name}")
    print(f"  Current Best:     {result.current_best_price} ({result.current_best_store})")
    print(f"  All-Time Low:     {result.all_time_low} ({result.all_time_low_store})")
    print()
    for sp in result.store_prices:
        print(f"  Store: {sp.store}")
        print(f"    Store Low:    {sp.store_low}")
        print(f"    Current:      {sp.current_price}")
        print(f"    Regular:      {sp.regular_price}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("isthereanydeal")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = DealSearchRequest()
            result = deal_search(page, request)
            print(f"\n=== DONE ===")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
