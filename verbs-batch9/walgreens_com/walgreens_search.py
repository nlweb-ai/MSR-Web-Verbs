"""Playwright script (Python) — Walgreens"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class WalgreensRequest:
    query: str = "allergy medicine"
    max_results: int = 5

@dataclass
class ProductItem:
    name: str = ""
    brand: str = ""
    price: str = ""
    num_reviews: str = ""

@dataclass
class WalgreensResult:
    products: List[ProductItem] = field(default_factory=list)

def search_walgreens(page: Page, request: WalgreensRequest) -> WalgreensResult:
    url = f"https://www.walgreens.com/search/results.jsp?Ntt={request.query.replace(' ', '+')}"
    checkpoint("Navigate to Walgreens search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = WalgreensResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: "Add to cart" delimiter. Walk back: name is before brand, brand before (reviews), then price.
        // Forward from name: brand → (reviews) → price (starts with $) or "Previous price was" → old price → "Current sale price is" → price
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'Add to cart' && i >= 5) {
                // Walk back to find name (long line with product details)
                let nameIdx = -1;
                for (let j = i - 1; j >= Math.max(0, i - 30); j--) {
                    // Name lines are long and contain the product details
                    if (lines[j].length > 30 && !lines[j].startsWith('$') && !lines[j].startsWith('(') &&
                        !lines[j].startsWith('Buy ') && !lines[j].startsWith('Pickup') &&
                        !lines[j].startsWith('Same Day') && !lines[j].startsWith('Shipping') &&
                        !lines[j].startsWith('available') && !lines[j].startsWith('Available') &&
                        !lines[j].startsWith('will open') && !lines[j].startsWith('Count:') &&
                        !lines[j].startsWith('Previous') && !lines[j].startsWith('Current') &&
                        !lines[j].startsWith('7 Days') && !lines[j].startsWith('Open ') &&
                        !/^\\d+$/.test(lines[j]) && lines[j] !== 'Add to cart') {
                        nameIdx = j;
                        break;
                    }
                }
                if (nameIdx < 0) continue;
                const name = lines[nameIdx];
                const brand = (nameIdx + 1 < lines.length) ? lines[nameIdx + 1] : '';
                let num_reviews = '';
                let price = '';
                for (let j = nameIdx + 2; j < Math.min(nameIdx + 10, i); j++) {
                    if (/^\\(\\d+\\)$/.test(lines[j])) {
                        num_reviews = lines[j].replace(/[()]/g, '');
                    }
                    if (lines[j].startsWith('$') && !price) {
                        price = lines[j].split('$')[1]; // first dollar amount
                        price = '$' + price;
                    }
                    if (lines[j] === 'Current sale price is' && j + 1 < lines.length) {
                        const saleLine = lines[j + 1];
                        if (saleLine.startsWith('$')) {
                            price = '$' + saleLine.split('$')[1];
                        }
                    }
                }
                results.push({ name, brand, price, num_reviews });
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
        print(f"  {i}. {p.name[:70]} - {p.brand} - {p.price} ({p.num_reviews} reviews)")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("walgreens")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_walgreens(page, WalgreensRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
