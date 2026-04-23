"""Playwright script (Python) — West Elm"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class WestElmRequest:
    query: str = "mid-century modern sofas"
    max_results: int = 5

@dataclass
class ProductItem:
    name: str = ""
    price: str = ""

@dataclass
class WestElmResult:
    products: List[ProductItem] = field(default_factory=list)

def search_westelm(page: Page, request: WestElmRequest) -> WestElmResult:
    url = f"https://www.westelm.com/search/results.html?words={request.query.replace(' ', '+')}"
    checkpoint("Navigate to West Elm search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = WestElmResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: "BEST SELLER"/"NEW" → Name → Name. → optional "LIMITED TIME OFFER" → "Sale price" → $ price
        // Or just name → name. → $ price
        const seen = new Set();
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if ((lines[i] === 'Sale price' || lines[i] === 'Starting at') && i + 1 < lines.length) {
                const priceLine = lines[i + 1];
                if (!priceLine.startsWith('$')) continue;
                const price = priceLine.replace(/\\s+/g, '');
                // Walk back for name
                let name = '';
                for (let j = i - 1; j >= Math.max(0, i - 6); j--) {
                    if (lines[j].endsWith(')') && lines[j].includes('(') && lines[j].length > 10 && !lines[j].endsWith(').')) {
                        name = lines[j];
                        break;
                    }
                }
                if (name && !seen.has(name)) {
                    seen.add(name);
                    results.push({ name, price });
                }
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = ProductItem()
        item.name = d.get("name", "")
        item.price = d.get("price", "")
        result.products.append(item)

    print(f"\nFound {len(result.products)} products:")
    for i, p in enumerate(result.products, 1):
        print(f"  {i}. {p.name} - {p.price}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("westelm")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_westelm(page, WestElmRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
