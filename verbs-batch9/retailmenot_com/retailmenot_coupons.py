"""Playwright script (Python) — RetailMeNot Coupons"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class RetailMeNotRequest:
    store: str = "nike.com"
    max_results: int = 5

@dataclass
class CouponItem:
    description: str = ""
    discount: str = ""
    offer_type: str = ""

@dataclass
class RetailMeNotResult:
    coupons: List[CouponItem] = field(default_factory=list)

def search_retailmenot(page: Page, request: RetailMeNotRequest) -> RetailMeNotResult:
    url = f"https://www.retailmenot.com/view/{request.store}"
    checkpoint("Navigate to RetailMeNot")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    result = RetailMeNotResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Coupons start after "VERIFIED OFFERS" line
        let start = 0;
        for (let i = 0; i < lines.length; i++) {
            if (/VERIFIED OFFERS/i.test(lines[i])) { start = i + 1; break; }
        }
        // Each coupon ends with "See Details"
        for (let i = start; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'See Details') {
                // Walk back to find description and discount
                let description = '', discount = '', offer_type = '';
                for (let j = i - 1; j >= start; j--) {
                    if (/interested users$/.test(lines[j])) {
                        // Description is the line before this
                        description = lines[j - 1] || '';
                        // offer_type is line before description
                        if (j - 2 >= start) offer_type = lines[j - 2] || '';
                        break;
                    }
                }
                // Find discount: walk back from description to find percentage
                for (let j = i - 1; j >= Math.max(start, i - 10); j--) {
                    if (/^\\d+%$/.test(lines[j]) || lines[j] === 'SALE' || lines[j] === 'FREE') {
                        if (lines[j] === 'SALE') discount = 'Sale';
                        else if (lines[j] === 'FREE') discount = 'Free';
                        else discount = lines[j] + ' off';
                        break;
                    }
                }
                if (description.length > 10) {
                    results.push({ description, discount, offer_type });
                }
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = CouponItem()
        item.description = d.get("description", "")
        item.discount = d.get("discount", "")
        item.offer_type = d.get("offer_type", "")
        result.coupons.append(item)

    print(f"\nFound {len(result.coupons)} coupons:")
    for i, c in enumerate(result.coupons, 1):
        print(f"\n  {i}. {c.description}")
        print(f"     Discount: {c.discount}  Type: {c.offer_type}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("retailmenot")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_retailmenot(page, RetailMeNotRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
