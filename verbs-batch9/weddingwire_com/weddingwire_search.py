"""Playwright script (Python) — WeddingWire"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class WeddingWireRequest:
    location: str = "Chicago, Illinois"
    max_results: int = 5

@dataclass
class PhotographerItem:
    name: str = ""
    rating: str = ""
    num_reviews: str = ""
    location: str = ""
    price: str = ""

@dataclass
class WeddingWireResult:
    photographers: List[PhotographerItem] = field(default_factory=list)

def search_weddingwire(page: Page, request: WeddingWireRequest) -> WeddingWireResult:
    city = request.location.lower().replace(', ', '-').replace(' ', '-')
    url = f"https://www.weddingwire.com/shared/search?search_type=2&geo_id=us-tx-austin"
    checkpoint("Navigate to WeddingWire vendors")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = WeddingWireResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: "Request pricing" delimiter. Walk back for name, rating, reviews, location, price.
        const skip = new Set(['Request pricing', 'Responds within 24 hours', 'List', 'Images', 'Map']);
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'Request pricing') {
                let name = '', rating = '', num_reviews = '', location = '', price = '';
                // Walk back to find name and fields
                for (let j = i - 1; j >= Math.max(0, i - 10); j--) {
                    if (lines[j].endsWith('starting price') && !price) {
                        price = lines[j];
                    }
                    if (/^\\d\\.\\d$/.test(lines[j]) && !rating) {
                        rating = lines[j];
                        name = lines[j - 1] || '';
                    }
                    if (/^\\(\\d+\\)$/.test(lines[j]) && !num_reviews) {
                        num_reviews = lines[j].replace(/[()]/g, '');
                    }
                    // Location: "City, ST" pattern
                    if (/,\\s+[A-Z]{2}$/.test(lines[j]) && !location) {
                        location = lines[j];
                        // If no rating found, name is the line before location (or before "·")
                        if (!name) {
                            for (let k = j - 1; k >= Math.max(0, j - 3); k--) {
                                if (lines[k] !== '\\u00b7' && !lines[k].startsWith('View ') &&
                                    lines[k] !== 'Popular with couples' && lines[k] !== 'Award winner' &&
                                    !skip.has(lines[k]) && lines[k].length > 2) {
                                    name = lines[k];
                                    break;
                                }
                            }
                        }
                    }
                }
                if (name) {
                    results.push({ name, rating, num_reviews, location, price });
                }
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = PhotographerItem()
        item.name = d.get("name", "")
        item.rating = d.get("rating", "")
        item.num_reviews = d.get("num_reviews", "")
        item.location = d.get("location", "")
        item.price = d.get("price", "")
        result.photographers.append(item)

    print(f"\nFound {len(result.photographers)} vendors:")
    for i, p in enumerate(result.photographers, 1):
        print(f"  {i}. {p.name} - {p.location} - {p.rating} ({p.num_reviews}) - {p.price}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("weddingwire")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_weddingwire(page, WeddingWireRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
