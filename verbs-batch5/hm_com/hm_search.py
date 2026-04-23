"""
Auto-generated Playwright script (Python)
hm.com – Clothing Search
Query: winter jacket

Generated on: 2026-04-18T01:05:31.603Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil, urllib.parse
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class HMSearchRequest:
    search_query: str = "winter jacket"
    max_results: int = 5


@dataclass(frozen=True)
class HMProduct:
    product_name: str = ""
    price: str = ""
    color_options: str = ""
    product_url: str = ""


@dataclass(frozen=True)
class HMSearchResult:
    products: list = None  # list[HMProduct]


def hm_search(page: Page, request: HMSearchRequest) -> HMSearchResult:
    """Search H&M for clothing items."""
    query = request.search_query
    max_results = request.max_results
    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    # ── Navigate to search ────────────────────────────────────────────
    url = f"https://www2.hm.com/en_us/search-results.html?q={urllib.parse.quote_plus(query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to H&M search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    # ── Extract products ──────────────────────────────────────────────
    checkpoint("Extract product listings")
    results_data = page.evaluate(r"""(maxResults) => {
        const articles = document.querySelectorAll('article');
        const results = [];
        for (const art of articles) {
            if (results.length >= maxResults) break;
            const h3 = art.querySelector('h3');
            if (!h3) continue;
            const name = h3.textContent.trim();
            const priceMatch = art.innerText.match(/\$(\d[\d,.]+)/);
            const price = priceMatch ? '$' + priceMatch[1] : '';
            const link = art.querySelector('a[href*="productpage"]');
            const url = link ? link.href : '';
            const colorMatch = art.innerText.match(/\+(\d+)/);
            const colors = colorMatch ? colorMatch[1] + '+ colors' : '1 color';
            results.push({ name, price, colors, url });
        }
        return results;
    }""", max_results)

    products = []
    for r in results_data:
        products.append(HMProduct(
            product_name=r.get("name", ""),
            price=r.get("price", ""),
            color_options=r.get("colors", ""),
            product_url=r.get("url", ""),
        ))

    # ── Print results ─────────────────────────────────────────────────
    print("=" * 60)
    print(f'H&M - "{query}" Products')
    print("=" * 60)
    for idx, p in enumerate(products, 1):
        print(f"\n{idx}. {p.product_name}")
        print(f"   Price: {p.price} | Colors: {p.color_options}")
        print(f"   URL: {p.product_url}")

    print(f"\nFound {len(products)} products")
    return HMSearchResult(products=products)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("hm_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = hm_search(page, HMSearchRequest())
            print(f"\nReturned {len(result.products or [])} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
