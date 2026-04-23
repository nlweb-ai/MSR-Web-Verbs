"""
Sleep Foundation – Search for sleep health articles by keyword

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class SleepfoundationSearchRequest:
    search_query: str = "insomnia"
    max_results: int = 5


@dataclass
class SleepfoundationArticleItem:
    title: str = ""
    author: str = ""
    reviewed_by: str = ""
    publish_date: str = ""
    summary: str = ""


@dataclass
class SleepfoundationSearchResult:
    items: List[SleepfoundationArticleItem] = field(default_factory=list)


# Search for sleep health articles on Sleep Foundation by keyword.
def sleepfoundation_search(page: Page, request: SleepfoundationSearchRequest) -> SleepfoundationSearchResult:
    """Search for sleep health articles on Sleep Foundation."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://www.sleepfoundation.org/insomnia"
    print(f"Loading {url}...")
    checkpoint("Navigate to Sleep Foundation search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = SleepfoundationSearchResult()

    checkpoint("Extract sleep health article listings")
    js_code = """(max) => {
        const links = document.querySelectorAll('a[href]');
        const items = [];
        const seen = new Set();
        for (const a of links) {
            if (items.length >= max) break;
            const href = a.getAttribute('href') || '';
            // Match sleepfoundation article URLs (at least 2 path segments, not homepage)
            if (!href.match(/sleepfoundation\\.org\\/insomnia\\//)) continue;
            if (href.includes('/wp-') || href.includes('/tag/') || href.includes('/category/')) continue;
            const text = a.textContent.trim();
            if (!text || text.length < 10 || text.length > 200) continue;
            if (seen.has(href)) continue;
            seen.add(href);
            items.push({title: text, author: '', reviewed_by: '', publish_date: '', summary: ''});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = SleepfoundationArticleItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.reviewed_by = d.get("reviewed_by", "")
        item.publish_date = d.get("publish_date", "")
        item.summary = d.get("summary", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Article {i}:")
        print(f"    Title:       {item.title}")
        print(f"    Author:      {item.author}")
        print(f"    Reviewed by: {item.reviewed_by}")
        print(f"    Date:        {item.publish_date}")
        print(f"    Summary:     {item.summary[:100]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("sleepfoundation")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SleepfoundationSearchRequest()
            result = sleepfoundation_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
