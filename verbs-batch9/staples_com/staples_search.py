"""Playwright script (Python) — Staples"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class StaplesRequest:
    query: str = "ergonomic office chairs"
    max_results: int = 5

@dataclass
class ProductItem:
    name: str = ""
    price: str = ""
    original_price: str = ""
    num_reviews: str = ""

@dataclass
class StaplesResult:
    products: List[ProductItem] = field(default_factory=list)

def search_staples(page: Page, request: StaplesRequest) -> StaplesResult:
    url = f"https://www.staples.com/{request.query.replace(' ', '+')}/directory_{request.query.replace(' ', '+')}"
    checkpoint("Navigate to Staples search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = StaplesResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        for (let i = 0; i < lines.length && results.length < max; i++) {
            // Pattern: "X% off" then skip image alt "of ...", then product name
            if (/^\\d+% off$/.test(lines[i])) {
                let j = i + 1;
                // Skip image alt line starting with "of "
                if (j < lines.length && lines[j].startsWith('of ')) j++;
                // Skip "In Demand!" line
                if (j < lines.length && lines[j].startsWith('In Demand!')) j++;
                const name = (j < lines.length) ? lines[j] : '';
                j++;
                // Skip Item/Model lines
                while (j < lines.length && (lines[j].startsWith('Item:') || lines[j].startsWith('Model:'))) j++;
                // Review count (just a number)
                const num_reviews = (j < lines.length && /^\\d+$/.test(lines[j])) ? lines[j] : '';
                if (num_reviews) j++;
                // "Price is" then actual price
                if (j < lines.length && lines[j] === 'Price is') j++;
                const price = (j < lines.length && lines[j].startsWith('$')) ? lines[j] : '';
                if (price) j++;
                // Original price line with "Regular price was"
                let original_price = '';
                if (j < lines.length && lines[j].includes('Regular price')) {
                    j++; // skip that line
                    if (j < lines.length && lines[j].startsWith('$')) {
                        original_price = lines[j];
                    }
                }
                if (name.length > 5 && !name.startsWith('Sponsored')) {
                    results.push({ name, price, original_price, num_reviews });
                }
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = ProductItem()
        item.name = d.get("name", "")
        item.price = d.get("price", "")
        item.original_price = d.get("original_price", "")
        item.num_reviews = d.get("num_reviews", "")
        result.products.append(item)

    print(f"\nFound {len(result.products)} products:")
    for i, p in enumerate(result.products, 1):
        print(f"  {i}. {p.name} - {p.price} (was {p.original_price}) [{p.num_reviews} reviews]")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("staples")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_staples(page, StaplesRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
