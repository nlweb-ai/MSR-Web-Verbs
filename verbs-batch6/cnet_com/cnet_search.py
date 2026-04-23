"""
Auto-generated Playwright script (Python)
CNET – Product Review Search
Query: "best laptops"

Generated on: 2026-04-18T05:06:04.868Z
Recorded 2 browser interactions
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
class ReviewRequest:
    query: str = "best laptops"
    max_results: int = 5


@dataclass
class Product:
    name: str = ""
    rating: str = ""
    price: str = ""
    summary: str = ""


@dataclass
class ReviewResult:
    products: list = field(default_factory=list)


def cnet_search(page: Page, request: ReviewRequest) -> ReviewResult:
    """Search CNET for product reviews."""
    print(f"  Query: {request.query}\n")

    # Navigate to CNET search page
    url = "https://www.cnet.com/search/"
    print(f"Loading {url} ...")
    checkpoint("Navigate to CNET search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # Type the query into the search input and submit
    checkpoint("Type search query")
    search_input = page.locator("#c-searchAutosuggest_input").first
    search_input.wait_for(state="visible", timeout=10000)
    search_input.click()
    page.wait_for_timeout(500)
    search_input.fill(request.query)
    page.wait_for_timeout(500)
    page.keyboard.press("Enter")

    # Wait for search results to render
    for attempt in range(10):
        page.wait_for_timeout(2000)
        result_count = page.evaluate("""() => {
            const container = document.querySelector('.c-pageSearch_searchResults, [class*="searchResults"]');
            return container ? container.children.length : 0;
        }""")
        print(f"  Poll {attempt+1}: {result_count} result children")
        if result_count > 0:
            break

    # Scroll to load lazy content
    for _ in range(3):
        page.evaluate("window.scrollBy(0, 600)")
        page.wait_for_timeout(800)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    checkpoint("Extract product listings")
    products_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();

        // Try the search results container first
        let container = document.querySelector('.c-pageSearch_searchResults, [class*="searchResults"]');
        if (!container) container = document.querySelector('main, #content, [role="main"]');
        if (!container) container = document.body;

        // Look for article/result items inside the results container
        const items = container.querySelectorAll('a[href]');
        for (const a of items) {
            if (results.length >= maxResults) break;
            const href = a.getAttribute('href') || '';
            if (href.length < 10) continue;

            const block = a.closest('article, li, section, [class*="item"], [class*="card"]') || a;
            const titleEl = block.querySelector('h2, h3, h4, [class*="title"], [class*="headline"]');
            let name = titleEl ? titleEl.innerText.trim() : '';
            if (!name) name = (a.getAttribute('aria-label') || a.innerText || '').trim();
            name = name.split('\n')[0].trim();
            if (!name || name.length < 10 || seen.has(name)) continue;
            if (/^(menu|sign|log|search|home|about|phones|laptops|audio|computers|services|deals|more)/i.test(name)) continue;
            seen.add(name);

            const text = block.innerText || '';
            let rating = '', price = '', summary = '';
            const ratM = text.match(/(\d+\.?\d*)\s*(?:\/\s*10|out of 10|stars?)/i);
            if (ratM) rating = ratM[1];
            const priceM = text.match(/\$(\d[\d,]*\.?\d*)/);
            if (priceM) price = "$" + priceM[1];
            const descEl = block.querySelector('p, [class*="desc"], [class*="dek"]');
            if (descEl) summary = descEl.innerText.trim().slice(0, 200);

            results.push({ name: name.slice(0, 120), rating, price, summary });
        }
        return results;
    }""", request.max_results)

    result = ReviewResult(products=[Product(**p) for p in products_data])

    print("\n" + "=" * 60)
    print(f"CNET: {request.query}")
    print("=" * 60)
    for p in result.products:
        print(f"  {p.name}")
        print(f"    Rating: {p.rating}  Price: {p.price}")
        print(f"    Summary: {p.summary[:80]}...")
    print(f"\n  Total: {len(result.products)} products")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("cnet_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = cnet_search(page, ReviewRequest())
            print(f"\nReturned {len(result.products)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
