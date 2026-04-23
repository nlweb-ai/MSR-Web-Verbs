"""Playwright script (Python) — Sephora"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class SephoraRequest:
    query: str = "moisturizer"
    max_results: int = 5

@dataclass
class ProductItem:
    name: str = ""
    brand: str = ""
    price: str = ""
    num_reviews: str = ""

@dataclass
class SephoraResult:
    products: List[ProductItem] = field(default_factory=list)

def search_sephora(page: Page, request: SephoraRequest) -> SephoraResult:
    url = f"https://www.sephora.com/search?keyword={request.query.replace(' ', '+')}"
    checkpoint("Navigate to Sephora search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = SephoraResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Products start after "Results for" line
        let start = 0;
        for (let i = 0; i < lines.length; i++) {
            if (/Results for/i.test(lines[i])) { start = i + 1; break; }
        }
        // Skip "Sort by" line
        if (start < lines.length && /^Sort by/i.test(lines[start])) start++;
        // Each product starts with "Quicklook", then Brand, Name, Colors, Reviews, Price
        for (let i = start; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'Quicklook' && i + 4 < lines.length) {
                const brand = lines[i + 1] || '';
                const name = lines[i + 2] || '';
                // Find review count and price
                let num_reviews = '', price = '';
                for (let j = i + 3; j < Math.min(i + 8, lines.length); j++) {
                    if (/^[\\d,.]+K?$/.test(lines[j])) { num_reviews = lines[j]; }
                    if (/^\\$/.test(lines[j])) { price = lines[j]; break; }
                }
                if (name.length > 3 && brand.length > 1) {
                    results.push({ name, brand, price, num_reviews });
                }
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = ProductItem()
        item.name = d.get("name", "")
        item.brand = d.get("brand", "")
        item.price = d.get("price", "")
        item.num_reviews = d.get("num_reviews", "")
        result.products.append(item)

    print(f"\nFound {len(result.products)} products:")
    for i, p in enumerate(result.products, 1):
        print(f"\n  {i}. {p.brand} - {p.name}")
        print(f"     Price: {p.price}  Reviews: {p.num_reviews}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("sephora")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_sephora(page, SephoraRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
