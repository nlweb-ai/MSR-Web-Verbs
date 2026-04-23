"""Playwright script (Python) — Target Circle Deals"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class TargetDealsRequest:
    category: str = "Electronics"
    max_results: int = 5

@dataclass
class DealItem:
    name: str = ""
    price: str = ""
    deal_description: str = ""

@dataclass
class TargetDealsResult:
    deals: List[DealItem] = field(default_factory=list)

def get_target_deals(page: Page, request: TargetDealsRequest) -> TargetDealsResult:
    url = "https://www.target.com/circle/deals"
    checkpoint("Navigate to Target Circle Deals")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = TargetDealsResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: price line (starts with $), optional deal description, product name, "Add to cart"
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'Add to cart') {
                // Walk back to find name (line before "Add to cart")
                let j = i - 1;
                if (j < 0) continue;
                const name = lines[j]; j--;
                // Look for deal description ("Buy...", "Save...", etc.) and price
                let deal_description = '';
                let price = '';
                while (j >= 0 && j >= i - 5) {
                    if (lines[j].startsWith('$')) {
                        if (!price) price = lines[j];
                    } else if (/^was /.test(lines[j])) {
                        // skip "was $X" lines - we prefer current price
                    } else if (/^Buy |^Save |^Get /.test(lines[j])) {
                        deal_description = lines[j];
                    }
                    j--;
                }
                if (name && name !== 'Highly rated' && !name.startsWith('$')) {
                    results.push({ name, price, deal_description });
                }
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = DealItem()
        item.name = d.get("name", "")
        item.price = d.get("price", "")
        item.deal_description = d.get("deal_description", "")
        result.deals.append(item)

    print(f"\nFound {len(result.deals)} deals:")
    for i, d in enumerate(result.deals, 1):
        print(f"  {i}. {d.name} - {d.price} | {d.deal_description}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("target_deals")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            get_target_deals(page, TargetDealsRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
