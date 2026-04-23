"""Playwright script (Python) — UNIQLO"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class UniqloRequest:
    query: str = "Ultra Light Down"
    max_results: int = 5

@dataclass
class ProductItem:
    name: str = ""
    price: str = ""
    rating: str = ""
    num_reviews: str = ""

@dataclass
class UniqloResult:
    products: List[ProductItem] = field(default_factory=list)

def search_uniqlo(page: Page, request: UniqloRequest) -> UniqloResult:
    url = f"https://www.uniqlo.com/us/en/search?q={request.query.replace(' ', '+')}"
    checkpoint("Navigate to UNIQLO search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = UniqloResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: "GENDER, SIZES" → Name → $Price → optional notes → rating → (count)
        // Stop at "Best Sellers" section
        const genderRe = /^(WOMEN|MEN|KIDS|BABY|UNISEX),\\s/;
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'Best Sellers' || lines[i] === 'SKIP') break;
            if (genderRe.test(lines[i]) && i + 2 < lines.length) {
                const name = lines[i + 1];
                const priceLine = lines[i + 2];
                if (!name || !priceLine.startsWith('$')) continue;
                let rating = '', num_reviews = '';
                // Scan forward for rating (number like 4.5) and review count (digits in parens)
                for (let j = i + 3; j < Math.min(i + 7, lines.length); j++) {
                    if (/^\\d\\.\\d$/.test(lines[j])) {
                        rating = lines[j];
                        if (j + 1 < lines.length && /^\\(\\d/.test(lines[j + 1])) {
                            num_reviews = lines[j + 1].replace(/[()]/g, '');
                        }
                        break;
                    }
                }
                results.push({ name, price: priceLine, rating, num_reviews });
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = ProductItem()
        item.name = d.get("name", "")
        item.price = d.get("price", "")
        item.rating = d.get("rating", "")
        item.num_reviews = d.get("num_reviews", "")
        result.products.append(item)

    print(f"\nFound {len(result.products)} products:")
    for i, p in enumerate(result.products, 1):
        print(f"  {i}. {p.name} - {p.price} - {p.rating} ({p.num_reviews} reviews)")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("uniqlo")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_uniqlo(page, UniqloRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
