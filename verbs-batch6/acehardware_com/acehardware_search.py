"""
Auto-generated Playwright script (Python)
Ace Hardware – Product Search
Query: "LED light bulbs"

Generated on: 2026-04-18T04:33:00.259Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
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
class ProductSearchRequest:
    query: str = "LED light bulbs"
    max_results: int = 5


@dataclass
class Product:
    product_name: str = ""
    brand: str = ""
    price: str = ""
    product_url: str = ""


@dataclass
class ProductSearchResult:
    products: list = field(default_factory=list)


def acehardware_search(page: Page, request: ProductSearchRequest) -> ProductSearchResult:
    """Search Ace Hardware for products."""
    print(f"  Query: {request.query}\n")

    # ── Navigate to Ace Hardware search ──────────────────────────────
    search_url = f"https://www.acehardware.com/search?query={quote_plus(request.query)}"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to Ace Hardware search")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Extract products from search results ─────────────────────────
    products = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();

        // Product cards in search results
        const cards = document.querySelectorAll('[data-testid="product-card"], .product-card, [class*="ProductCard"], li[class*="product"]');
        for (const card of cards) {
            if (results.length >= maxResults) break;

            // Product name - look for link with product title
            let name = '';
            const nameEl = card.querySelector('a[data-testid="product-name"], [class*="product-name"], [class*="ProductName"], h2 a, h3 a, a[href*="/product/"]');
            if (nameEl) name = nameEl.innerText.trim();
            if (!name) {
                const heading = card.querySelector('h2, h3, h4');
                if (heading) name = heading.innerText.trim();
            }
            if (!name || name.length < 3 || seen.has(name)) continue;
            seen.add(name);

            // Product URL
            let url = '';
            const linkEl = card.querySelector('a[href*="/product/"]') || card.querySelector('a[href]');
            if (linkEl) {
                url = linkEl.href || '';
                if (url && !url.startsWith('http')) url = 'https://www.acehardware.com' + url;
            }

            // Brand
            let brand = '';
            const brandEl = card.querySelector('[data-testid="product-brand"], [class*="brand"], [class*="Brand"]');
            if (brandEl) brand = brandEl.innerText.trim();

            // Price
            let price = '';
            const priceEl = card.querySelector('[data-testid="product-price"], [class*="price"], [class*="Price"], span[class*="sale"], span[class*="retail"]');
            if (priceEl) {
                price = priceEl.innerText.trim().split('\n')[0];
            }
            if (!price) {
                const allText = card.innerText || '';
                const priceMatch = allText.match(/\$[\d,]+\.?\d*/);
                if (priceMatch) price = priceMatch[0];
            }

            results.push({
                product_name: name.slice(0, 150),
                brand: brand,
                price: price,
                product_url: url,
            });
        }

        // Fallback: try generic product listing selectors
        if (results.length === 0) {
            const links = document.querySelectorAll('a[href*="/product/"]');
            for (const link of links) {
                if (results.length >= maxResults) break;
                const name = link.innerText.trim();
                if (!name || name.length < 5 || seen.has(name)) continue;
                seen.add(name);
                let url = link.href || '';
                if (url && !url.startsWith('http')) url = 'https://www.acehardware.com' + url;
                const container = link.closest('li, div[class*="product"], div[class*="card"]') || link.parentElement;
                let price = '';
                if (container) {
                    const priceMatch = (container.innerText || '').match(/\$[\d,]+\.?\d*/);
                    if (priceMatch) price = priceMatch[0];
                }
                results.push({ product_name: name.slice(0, 150), brand: '', price: price, product_url: url });
            }
        }
        return results;
    }""", request.max_results)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Ace Hardware: {request.query}")
    print("=" * 60)
    for idx, p in enumerate(products, 1):
        print(f"\n  {idx}. {p['product_name']}")
        print(f"     Brand: {p['brand']}")
        print(f"     Price: {p['price']}")
        print(f"     URL: {p['product_url']}")

    result_products = [Product(**p) for p in products]
    print(f"\nFound {len(result_products)} products")
    return ProductSearchResult(products=result_products)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("acehardware_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = acehardware_search(page, ProductSearchRequest())
            print(f"\nReturned {len(result.products)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
