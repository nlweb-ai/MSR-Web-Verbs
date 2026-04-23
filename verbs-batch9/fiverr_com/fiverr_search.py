"""
Playwright script (Python) — Fiverr Gig Search
Search for freelancer gigs on Fiverr.com.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class FiverrSearchRequest:
    search_query: str = "logo design"
    max_results: int = 5


@dataclass
class GigItem:
    title: str = ""
    seller: str = ""
    level: str = ""
    price: str = ""
    rating: str = ""
    reviews: str = ""


@dataclass
class FiverrSearchResult:
    query: str = ""
    items: List[GigItem] = field(default_factory=list)


# Searches Fiverr.com for gigs matching the query and returns up to max_results
# gigs with title, seller name, seller level, price, rating, and review count.
def search_fiverr_gigs(page: Page, request: FiverrSearchRequest) -> FiverrSearchResult:
    import urllib.parse
    url = f"https://www.fiverr.com/search/gigs?query={urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = FiverrSearchResult(query=request.search_query)

    checkpoint("Extract gig listings")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        const cards = document.querySelectorAll('[class*="gig-card"], [class*="GigCard"]');
        for (const card of cards) {
            if (results.length >= max) break;
            const lines = card.innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 5) continue;
            // Find the title line (longest line > 20 chars)
            let titleIdx = -1;
            for (let i = 0; i < lines.length; i++) {
                if (lines[i].length > 20) { titleIdx = i; break; }
            }
            if (titleIdx < 0) continue;
            const title = lines[titleIdx].trim();
            if (seen.has(title)) continue;
            seen.add(title);
            // Seller name is usually 1-2 lines before title
            const seller = (titleIdx >= 2) ? lines[titleIdx - 2].trim() : '';
            const level = (titleIdx >= 1) ? lines[titleIdx - 1].trim() : '';
            // After title: rating, reviews (in parens), price
            let rating = '', reviews = '', price = '';
            for (let i = titleIdx + 1; i < lines.length; i++) {
                const l = lines[i].trim();
                if (l.match(/^[0-9]\.[0-9]$/)) rating = l;
                if (l.match(/^\([0-9,]+\)$/) || l.match(/^\([0-9.]+k?\)$/)) reviews = l.replace(/[()]/g, '');
                if (l.includes('$') && l.match(/\\$[0-9]/)) price = l.replace(/\\u00a0/g, ' ');
            }
            results.push({title, seller, level, price, rating, reviews});
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = GigItem()
        item.title = d.get("title", "")
        item.seller = d.get("seller", "")
        item.level = d.get("level", "")
        item.price = d.get("price", "")
        item.rating = d.get("rating", "")
        item.reviews = d.get("reviews", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} gigs for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Seller: {item.seller}  Level: {item.level}  Price: {item.price}")
        print(f"     Rating: {item.rating}  Reviews: {item.reviews}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("fiverr")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_fiverr_gigs(page, FiverrSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} gigs")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
