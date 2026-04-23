"""
Auto-generated Playwright script (Python)
Farfetch – Search products

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
class SearchRequest:
    search_query: str = "Gucci bags"
    max_results: int = 5


@dataclass
class Product:
    brand: str = ""
    product_name: str = ""
    price: str = ""
    url: str = ""


@dataclass
class SearchResult:
    products: List[Product] = field(default_factory=list)


def farfetch_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search Farfetch and extract product results."""
    print(f"  Query: {request.search_query}\n")

    encoded = quote_plus(request.search_query)
    url = f"https://www.farfetch.com/shopping/women/search/items.aspx?q={encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Farfetch search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = SearchResult()

    checkpoint("Extract product cards")
    products_data = page.evaluate(
        r"""(max) => {
            const cards = document.querySelectorAll('[data-testid="productCard"]');
            const items = [];
            for (let i = 0; i < cards.length && items.length < max; i++) {
                const card = cards[i];
                const text = card.innerText.trim();
                const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);

                // Filter out labels like "New Season", "15% off"
                const dataLines = lines.filter(l => 
                    l !== 'New Season' && !l.includes('% off') && 
                    l !== 'Available' && l !== 'See all sizes'
                );

                // Structure: brand, product_name, price
                const brand = dataLines[0] || '';
                const productName = dataLines[1] || '';
                const price = dataLines.find(l => l.startsWith('$')) || '';

                const link = card.querySelector('a[data-component="ProductCardLink"]');
                const href = link ? link.href : '';

                if (brand && productName) {
                    items.push({brand, product_name: productName, price, url: href});
                }
            }
            return items;
        }""",
        request.max_results,
    )

    for d in products_data:
        product = Product()
        product.brand = d.get("brand", "")
        product.product_name = d.get("product_name", "")
        product.price = d.get("price", "")
        product.url = d.get("url", "")
        result.products.append(product)

    for i, p in enumerate(result.products, 1):
        print(f"\n  Product {i}:")
        print(f"    Brand:   {p.brand}")
        print(f"    Name:    {p.product_name}")
        print(f"    Price:   {p.price}")
        print(f"    URL:     {p.url}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("farfetch")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = farfetch_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.products)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
