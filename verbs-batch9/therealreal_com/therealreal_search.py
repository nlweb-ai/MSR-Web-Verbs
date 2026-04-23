"""Playwright script (Python) — The RealReal"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class TheRealRealRequest:
    designer: str = "Gucci"
    max_results: int = 5

@dataclass
class ConsignmentItem:
    name: str = ""
    designer: str = ""
    price: str = ""
    discount: str = ""

@dataclass
class TheRealRealResult:
    items: List[ConsignmentItem] = field(default_factory=list)

def search_therealreal(page: Page, request: TheRealRealRequest) -> TheRealRealResult:
    url = f"https://www.therealreal.com/designers/{request.designer.lower()}"
    checkpoint("Navigate to The RealReal")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = TheRealRealResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: "- Price:" then "$X" — name is 2-3 lines above
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i] === '- Price:' && i + 1 < lines.length) {
                const price = lines[i + 1];
                // Walk back to find name (skip "Size:", "% Off", "ON HOLD", "See Similar")
                let j = i - 1;
                let discount = '';
                let name = '';
                while (j >= 0 && j >= i - 5) {
                    if (/Off Est\\. Retail/.test(lines[j])) {
                        discount = lines[j];
                    } else if (!lines[j].startsWith('Size:') && lines[j] !== 'ON HOLD' && lines[j] !== 'See Similar' && lines[j].length > 3 && !/^Gucci$/.test(lines[j])) {
                        name = lines[j];
                        break;
                    }
                    j--;
                }
                if (name) {
                    results.push({ name, designer: 'Gucci', price, discount });
                }
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = ConsignmentItem()
        item.name = d.get("name", "")
        item.designer = d.get("designer", "")
        item.price = d.get("price", "")
        item.discount = d.get("discount", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} items:")
    for i, it in enumerate(result.items, 1):
        disc = f" ({it.discount})" if it.discount else ""
        print(f"  {i}. {it.name} - {it.price}{disc}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("therealreal")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_therealreal(page, TheRealRealRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
