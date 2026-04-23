"""
Auto-generated Playwright script (Python)
Menards – Product Search
Query: "cordless drill"

Generated on: 2026-04-18T15:10:44.351Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ProductRequest:
    query: str = "cordless drill"
    max_results: int = 5


@dataclass
class Product:
    name: str = ""
    brand: str = ""
    price: str = ""
    rating: str = ""
    url: str = ""


@dataclass
class ProductResult:
    products: List[Product] = field(default_factory=list)


def menards_search(page: Page, request: ProductRequest) -> ProductResult:
    """Search Menards for products."""
    print(f"  Query: {request.query}\n")

    # ── Step 1: Navigate to Menards homepage ──────────────────────────
    print("Loading Menards homepage...")
    checkpoint("Navigate to Menards homepage")
    page.goto("https://www.menards.com/", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)

    # ── Step 2: Search using the search form ──────────────────────────
    checkpoint("Search for products")
    search_input = page.locator('input[data-testid="search-input"], input[aria-label*="search" i], input[name="search"]').first
    search_input.fill(request.query)
    page.wait_for_timeout(500)
    search_input.press("Enter")
    page.wait_for_timeout(8000)

    # ── Step 3: Parse product listings from body text ─────────────────
    checkpoint("Extract product listings")
    items = page.evaluate(r"""(maxResults) => {
        const text = document.body.innerText;
        const results = [];

        // Products are separated by "Compare\n" markers in the text
        // Pattern: "Compare\nProductName\nSku # XXXX\n...\nPRICE/SALE PRICE\n$XX.XX"
        const blocks = text.split(/\nCompare\n/);

        for (let i = 1; i < blocks.length && results.length < maxResults; i++) {
            const block = blocks[i];
            const lines = block.split('\n').map(l => l.trim()).filter(Boolean);
            if (lines.length < 3) continue;

            const name = lines[0] || '';
            if (!name || name.length < 5) continue;

            // Extract brand from the first word/brand name pattern
            const brand = name.match(/^([A-Za-z+®™&]+(?:[\s]+[A-Za-z+®™&]+)?)/)?.[1] || '';

            // Find price - look for "$XX.XX" pattern
            let price = '';
            for (const line of lines) {
                const priceMatch = line.match(/^\$[\d,.]+$/);
                if (priceMatch) {
                    price = priceMatch[0];
                    break;
                }
            }

            results.push({ name, brand, price });
        }
        return results;
    }""", request.max_results)

    result = ProductResult(products=[Product(
        name=p['name'], brand=p['brand'], price=p['price']
    ) for p in items])

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Menards: \"{request.query}\"")
    print("=" * 60)
    for i, p in enumerate(items, 1):
        print(f"\n  {i}. {p['name']}")
        print(f"     Brand: {p['brand']}  |  Price: {p['price']}")
    if not any(p.get('rating') for p in items):
        print("\n  Note: Ratings not shown on Menards search results page")
    print(f"\n  Total: {len(items)} products")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("menards_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = menards_search(page, ProductRequest())
            print(f"\nReturned {len(result.products)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
