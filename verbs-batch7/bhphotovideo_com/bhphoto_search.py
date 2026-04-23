"""
Auto-generated Playwright script (Python)
B&H Photo – Product Search
Query: "Sony A7 IV"

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ProductSearchRequest:
    search_query: str = "Sony A7 IV"
    max_products: int = 5


@dataclass
class Product:
    product_name: str = ""
    price: str = ""
    customer_rating: str = ""
    availability: str = ""


@dataclass
class ProductSearchResult:
    products: List[Product] = field(default_factory=list)


def bhphoto_search(page: Page, request: ProductSearchRequest) -> ProductSearchResult:
    """Search B&H Photo for products."""
    print(f"  Query: {request.search_query}\n")

    # ── Navigate to search results ────────────────────────────────────
    query = quote_plus(request.search_query)
    url = f"https://www.bhphotovideo.com/c/search?q={query}"
    print(f"Loading {url}...")
    checkpoint("Navigate to B&H Photo search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = ProductSearchResult()

    # ── Extract products from search results ──────────────────────────
    checkpoint("Extract product list")
    products_data = page.evaluate("""(maxProducts) => {
        const results = [];
        const cards = document.querySelectorAll('[data-selenium="miniProductPage"]');
        for (let i = 0; i < Math.min(cards.length, maxProducts); i++) {
            const card = cards[i];
            const text = card.innerText;

            // Product name from title link
            const nameEl = card.querySelector('[data-selenium="miniProductPageName"]') ||
                           card.querySelector('[data-selenium="miniProductPageProductImgLink"]');
            const name = nameEl ? nameEl.innerText.trim() || nameEl.getAttribute('aria-label') || '' : '';

            // Price
            const priceEl = card.querySelector('[data-selenium="uppedDecimalPriceFirst"]') ||
                            card.querySelector('[class*="price"]');
            let price = priceEl ? priceEl.innerText.trim() : '';
            const centsEl = card.querySelector('[data-selenium="uppedDecimalPriceSecond"]');
            if (centsEl) price += centsEl.innerText.trim();

            // Rating
            let rating = '';
            const reviewMatch = text.match(/(\\d+)\\s*Reviews?/i);
            if (reviewMatch) rating = reviewMatch[1] + ' Reviews';

            // Availability
            let availability = '';
            if (text.includes('In Stock')) availability = 'In Stock';
            else if (text.includes('Backordered')) availability = 'Backordered';
            else if (text.includes('New Item')) availability = 'New Item';
            else if (text.includes('Pre-Order')) availability = 'Pre-Order';

            if (name) results.push({name, price, rating, availability});
        }
        return results;
    }""", request.max_products)

    for pd in products_data:
        product = Product()
        product.product_name = pd.get("name", "")
        product.price = pd.get("price", "")
        product.customer_rating = pd.get("rating", "")
        product.availability = pd.get("availability", "")
        result.products.append(product)

    # ── Print results ─────────────────────────────────────────────────
    for i, p in enumerate(result.products, 1):
        print(f"\n  Product {i}:")
        print(f"    Name:         {p.product_name}")
        print(f"    Price:        {p.price}")
        print(f"    Rating:       {p.customer_rating}")
        print(f"    Availability: {p.availability}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("bhphoto")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = ProductSearchRequest()
            result = bhphoto_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.products)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
