"""
Auto-generated Playwright script (Python)
michaels.com – Product Search
Query: acrylic paint set

Generated on: 2026-04-18T01:35:33.143Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MichaelsRequest:
    query: str = "acrylic paint set"
    max_results: int = 5


@dataclass(frozen=True)
class MichaelsProduct:
    product_name: str = ""
    brand: str = ""
    price: str = ""
    rating: str = ""
    availability: str = ""


@dataclass(frozen=True)
class MichaelsResult:
    products: list = None  # list[MichaelsProduct]


def michaels_search(page: Page, request: MichaelsRequest) -> MichaelsResult:
    """Search Michaels for products."""
    query = request.query
    print(f"  Query: {query}\n")

    # ── Navigate to search page ───────────────────────────────────────
    url = f"https://www.michaels.com/search?q={query.replace(' ', '+')}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Michaels search results")
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(12000)

    # ── Extract products ──────────────────────────────────────────────
    products = page.evaluate(r"""(maxResults) => {
        const nameEls = document.querySelectorAll('[class*="product-name-container"]');
        const results = [];
        for (let i = 0; i < Math.min(nameEls.length, maxResults); i++) {
            const nameEl = nameEls[i];
            const h3 = nameEl.querySelector('h3');
            const fullName = h3 ? h3.innerText.trim() : '';

            // Parse brand from name ("... by Brand®")
            let productName = fullName;
            let brand = '';
            const byMatch = fullName.match(/^(.+?)\s+by\s+(.+)$/);
            if (byMatch) {
                productName = byMatch[1];
                brand = byMatch[2];
            } else {
                // Brand might be prefix (e.g., "DecoArt® ...")
                const prefixMatch = fullName.match(/^([\w]+[®™]*)\s+/);
                if (prefixMatch) brand = prefixMatch[1];
            }

            // Navigate up to card container
            let card = nameEl;
            for (let j = 0; j < 6; j++) {
                card = card.parentElement;
                if (!card) break;
                const text = card.innerText;
                if (text.includes('Store Pickup') || text.includes('Add to Cart')) break;
            }
            if (!card) continue;
            const text = card.innerText;

            // Rating from Bazaarvoice aria-label
            const ratingEl = card.querySelector('[class*="bv_inline_rating_container"]');
            let rating = '';
            if (ratingEl) {
                const aria = ratingEl.getAttribute('aria-label') || '';
                const ratingMatch = aria.match(/([d.]+)\s+out of\s+5/);
                if (ratingMatch) rating = ratingMatch[1] + '/5';
            }

            // Price
            const priceEl = card.querySelector('[class*="price-text"]:not([class*="unit-price"])');
            const price = priceEl ? priceEl.innerText.trim() : '';

            // Availability from Store Pickup line
            let availability = '';
            const lines = text.split('\n');
            for (let k = 0; k < lines.length; k++) {
                if (lines[k].trim() === 'Store Pickup') {
                    const nextLine = lines[k + 2] || '';
                    if (nextLine.includes('In Stock')) availability = nextLine.trim();
                    else if (nextLine.includes('Unavailable')) availability = 'Unavailable';
                    else availability = nextLine.trim();
                    break;
                }
            }

            results.push({ product_name: productName, brand, price, rating, availability });
        }
        return results;
    }""", request.max_results)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f'Michaels - "{request.query}" Products')
    print("=" * 60)
    for idx, p in enumerate(products, 1):
        print(f"\n  {idx}. {p['product_name']}")
        if p['brand']:
            print(f"     Brand: {p['brand']}")
        print(f"     Price: {p['price']}")
        if p['rating']:
            print(f"     Rating: {p['rating']}")
        print(f"     Availability: {p['availability']}")

    print(f"\nFound {len(products)} products")
    return MichaelsResult(
        products=[MichaelsProduct(**p) for p in products]
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("michaels_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = michaels_search(page, MichaelsRequest())
            print(f"\nReturned {len(result.products or [])} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
