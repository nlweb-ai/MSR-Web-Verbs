"""
Playwright script (Python) — Delish Search
Search Delish for recipes matching a query.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class DelishSearchRequest:
    search_query: str = "slow cooker"
    max_results: int = 5


@dataclass
class RecipeItem:
    name: str = ""
    total_time: str = ""
    description: str = ""


@dataclass
class DelishSearchResult:
    query: str = ""
    items: List[RecipeItem] = field(default_factory=list)


def search_delish(page: Page, request: DelishSearchRequest) -> DelishSearchResult:
    """Search Delish for recipes."""
    url = f"https://www.delish.com/search/?q={request.search_query.replace(' ', '+')}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = DelishSearchResult(query=request.search_query)

    checkpoint("Extract recipes")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('a[href*="/recipe"], .search-result, [class*="result"], article');
        for (const card of cards) {
            if (items.length >= max) break;
            const text = (card.textContent || '').replace(/\\s+/g, ' ').trim();

            let name = '';
            const nameEl = card.querySelector('h2, h3, [class*="title"], [class*="name"]');
            if (nameEl) name = nameEl.textContent.trim();
            if (!name || name.length < 3) continue;
            if (items.some(i => i.name === name)) continue;

            let totalTime = '';
            const timeMatch = text.match(/(\\d+)\\s*(?:min|hour|hr)/i);
            if (timeMatch) totalTime = timeMatch[0];



            let desc = '';
            const descEl = card.querySelector('p, [class*="dek"], [class*="desc"]');
            if (descEl) desc = descEl.textContent.trim().substring(0, 200);

            items.push({name, total_time: totalTime, description: desc});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = RecipeItem()
        item.name = d.get("name", "")
        item.total_time = d.get("total_time", "")
        item.description = d.get("description", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} recipes for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name}")
        print(f"     Time: {item.total_time}")
        if item.description:
            print(f"     {item.description[:100]}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("delish")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_delish(page, DelishSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} recipes")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
