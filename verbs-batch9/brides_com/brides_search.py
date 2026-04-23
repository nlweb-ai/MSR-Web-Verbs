"""
Playwright script (Python) — Brides Search
Search for articles on Brides.com.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BridesSearchRequest:
    query: str = "outdoor wedding ideas"
    max_results: int = 5


@dataclass
class ArticleItem:
    title: str = ""


@dataclass
class BridesSearchResult:
    query: str = ""
    items: List[ArticleItem] = field(default_factory=list)


def search_brides(page: Page, request: BridesSearchRequest) -> BridesSearchResult:
    """Search Brides.com for articles."""
    encoded = quote_plus(request.query)
    url = f"https://www.brides.com/search?q={encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = BridesSearchResult(query=request.query)

    checkpoint("Extract articles")
    js_code = """(max) => {
        const items = [];
        const content = document.querySelector('.search-results__content');
        if (!content) return items;
        const links = content.querySelectorAll('a');
        for (const a of links) {
            if (items.length >= max) break;
            const title = a.innerText.trim();
            if (!title || title.length < 10 || title.length > 300) continue;
            if (items.some(i => i.title === title)) continue;
            items.push({title: title});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ArticleItem()
        item.title = d.get("title", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} articles for '{request.query}':")
    for i, item in enumerate(result.items, 1):
        print(f"  {i}. {item.title}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("brides")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_brides(page, BridesSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
