"""Playwright script (Python) — The Knot"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class TheKnotRequest:
    location: str = "Austin, Texas"
    max_results: int = 5

@dataclass
class VenueItem:
    name: str = ""
    capacity: str = ""
    price_range: str = ""
    rating: str = ""
    num_reviews: str = ""

@dataclass
class TheKnotResult:
    venues: List[VenueItem] = field(default_factory=list)

def search_theknot(page: Page, request: TheKnotRequest) -> TheKnotResult:
    url = "https://www.theknot.com/marketplace/wedding-reception-venues-austin-tx"
    checkpoint("Navigate to The Knot venues")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    page.evaluate("window.scrollBy(0, 800)")
    page.wait_for_timeout(5000)
    result = TheKnotResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: "Vendor Details" block → Location → rating → Stars → (count) → Reviews → Name → "Starting at $X" → capacity
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i] !== 'Vendor Details') continue;
            // Skip Location block, find rating/Reviews
            let j = i + 1;
            let rating = '', num_reviews = '';
            let isNew = false;
            // Advance past Location:/city/state
            while (j < lines.length && j < i + 8) {
                if (/^\\d+\\.\\d+$/.test(lines[j]) || lines[j] === '0') {
                    rating = lines[j]; break;
                }
                if (lines[j] === 'New') { isNew = true; j++; break; }
                j++;
            }
            if (!isNew) {
                // Find "Reviews" line to locate review count
                while (j < lines.length && j < i + 12) {
                    if (lines[j] === 'Reviews') {
                        // Count is the line before "Reviews" like "(39)"
                        if (j >= 1) num_reviews = lines[j - 1].replace(/[()]/g, '');
                        j++;
                        break;
                    }
                    j++;
                }
            }
            // Name is next non-empty line after Reviews
            if (j >= lines.length) continue;
            const name = lines[j]; j++;
            // "Starting at $X" or capacity line
            let price_range = '', capacity = '';
            if (j < lines.length && lines[j].startsWith('Starting at')) {
                price_range = lines[j].replace('Starting at ', ''); j++;
            }
            // Deals line (skip)
            if (j < lines.length && /^\\d+ Deals?$/.test(lines[j])) j++;
            // Capacity line like "300+ Guests..."
            if (j < lines.length && /Guests/.test(lines[j])) {
                capacity = lines[j].split('\\u2022')[0].trim();
            }
            if (name && name.length > 3 && !/^Vendor|^Location|^Stars|, TX$|, CA$|, NY$|, FL$/.test(name)) {
                results.push({ name, capacity, price_range, rating, num_reviews });
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = VenueItem()
        item.name = d.get("name", "")
        item.capacity = d.get("capacity", "")
        item.price_range = d.get("price_range", "")
        item.rating = d.get("rating", "")
        item.num_reviews = d.get("num_reviews", "")
        result.venues.append(item)

    print(f"\nFound {len(result.venues)} venues:")
    for i, v in enumerate(result.venues, 1):
        print(f"  {i}. {v.name} | {v.rating} ({v.num_reviews}) | {v.price_range} | {v.capacity}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("theknot")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_theknot(page, TheKnotRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
