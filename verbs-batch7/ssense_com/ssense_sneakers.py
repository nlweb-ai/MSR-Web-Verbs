"""
Auto-generated Playwright script (Python)
SSENSE – Designer Sneaker Search

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class SearchRequest:
    category_url: str = "https://www.ssense.com/en-us/men/shoes/sneakers"
    max_results: int = 5


@dataclass
class ProductResult:
    brand: str = ""
    product_name: str = ""
    price: str = ""


@dataclass
class SearchResult:
    products: List[ProductResult] = field(default_factory=list)


def ssense_sneakers(page: Page, request: SearchRequest) -> SearchResult:
    """Extract designer sneakers from SSENSE."""
    print(f"  Category: {request.category_url}\n")

    print(f"Loading {request.category_url}...")
    checkpoint("Navigate to category")
    page.goto(request.category_url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = SearchResult()

    checkpoint("Extract product listings")
    js_code = r"""(max) => {
        const body = document.body.innerText;
        const lines = body.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find "SHOES FOR MEN" description block end - products start after the long description
        let startIdx = 0;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].startsWith('SHOES FOR MEN')) {
                // Skip the description paragraph
                startIdx = i + 2;
                break;
            }
        }
        const pricePattern = /^\$[\d,]+$/;
        const products = [];
        let i = startIdx;
        while (i < lines.length && products.length < max) {
            const brand = lines[i];
            i++;
            if (i >= lines.length) break;
            const name = lines[i];
            i++;
            if (i >= lines.length) break;
            const price = lines[i];
            i++;
            if (brand && name && pricePattern.test(price)) {
                products.push({brand, product_name: name, price});
            }
        }
        return products;
    }"""
    products_data = page.evaluate(js_code, request.max_results)

    for pd in products_data:
        p = ProductResult()
        p.brand = pd.get("brand", "")
        p.product_name = pd.get("product_name", "")
        p.price = pd.get("price", "")
        result.products.append(p)

    for i, p in enumerate(result.products, 1):
        print(f"\n  Product {i}:")
        print(f"    Brand:   {p.brand}")
        print(f"    Name:    {p.product_name}")
        print(f"    Price:   {p.price}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("ssense")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = ssense_sneakers(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.products)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
