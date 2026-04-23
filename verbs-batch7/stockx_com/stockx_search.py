"""
Auto-generated Playwright script (Python)
StockX – Sneaker Search

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class SearchRequest:
    search_query: str = "Nike Air Jordan 1 Retro"
    max_results: int = 5


@dataclass
class ShoeResult:
    shoe_name: str = ""
    lowest_ask: str = ""


@dataclass
class SearchResult:
    shoes: List[ShoeResult] = field(default_factory=list)


def stockx_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search StockX for sneakers."""
    print(f"  Query: {request.search_query}\n")

    query_encoded = request.search_query.replace(" ", "+")
    url = f"https://stockx.com/search?s={query_encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = SearchResult()

    checkpoint("Extract search results")
    js_code = r"""(max) => {
        const body = document.body.innerText;
        const lines = body.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find "results for" line
        let startIdx = 0;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].match(/results for|Clear All/)) {
                startIdx = i + 1;
                break;
            }
        }
        // Skip "Search: ..." and "Clear All" lines
        while (startIdx < lines.length && (lines[startIdx].startsWith('Search:') || lines[startIdx] === 'Clear All')) startIdx++;
        const shoes = [];
        let i = startIdx;
        while (i < lines.length && shoes.length < max) {
            const name = lines[i];
            if (!name || name === 'Our Process' || /^\d+$/.test(name)) break;
            i++;
            if (i >= lines.length) break;
            // Next should be "Lowest Ask" or size info
            let price = '';
            while (i < lines.length) {
                const l = lines[i];
                if (l.startsWith('$') || l === '--') {
                    price = l;
                    i++;
                    break;
                }
                i++;
            }
            // Skip "Xpress Ship" or "Sponsored" if present
            while (i < lines.length && (lines[i] === 'Xpress Ship' || lines[i] === 'Sponsored')) i++;
            if (name && price) {
                shoes.push({shoe_name: name, lowest_ask: price});
            }
        }
        return shoes;
    }"""
    shoes_data = page.evaluate(js_code, request.max_results)

    for sd in shoes_data:
        s = ShoeResult()
        s.shoe_name = sd.get("shoe_name", "")
        s.lowest_ask = sd.get("lowest_ask", "")
        result.shoes.append(s)

    for i, s in enumerate(result.shoes, 1):
        print(f"\n  Shoe {i}:")
        print(f"    Name:       {s.shoe_name}")
        print(f"    Lowest Ask: {s.lowest_ask}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("stockx")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = stockx_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.shoes)} shoes")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
