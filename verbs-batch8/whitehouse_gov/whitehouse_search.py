"""
White House – Search for official briefings and statements

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
class WhitehouseSearchRequest:
    search_query: str = "executive order"
    max_results: int = 5


@dataclass
class WhitehouseBriefingItem:
    title: str = ""
    publish_date: str = ""
    category: str = ""
    summary: str = ""
    url: str = ""


@dataclass
class WhitehouseSearchResult:
    items: List[WhitehouseBriefingItem] = field(default_factory=list)


def whitehouse_search(page: Page, request: WhitehouseSearchRequest) -> WhitehouseSearchResult:
    """Search for official White House briefings and statements."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://www.whitehouse.gov/?s={query}"
    print(f"Loading {url}...")
    checkpoint("Navigate to White House search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = WhitehouseSearchResult()

    checkpoint("Extract briefing listings")
    js_code = """(max) => {
        const cards = document.querySelectorAll('article, [class*="result"], [class*="briefing"], [class*="news"], [class*="post"], .wp-block-post');
        const items = [];
        for (const card of cards) {
            if (items.length >= max) break;
            const titleEl = card.querySelector('h2, h3, [class*="title"], [class*="headline"]');
            const dateEl = card.querySelector('time, [class*="date"], [class*="time"]');
            const categoryEl = card.querySelector('[class*="category"], [class*="type"], [class*="label"], [class*="tag"]');
            const summaryEl = card.querySelector('p, [class*="description"], [class*="summary"], [class*="excerpt"]');
            const linkEl = card.querySelector('a[href]') || titleEl?.closest('a') || titleEl?.querySelector('a');

            const title = titleEl ? titleEl.textContent.trim() : '';
            const publish_date = dateEl ? (dateEl.getAttribute('datetime') || dateEl.textContent.trim()) : '';
            const category = categoryEl ? categoryEl.textContent.trim() : '';
            const summary = summaryEl ? summaryEl.textContent.trim() : '';
            const url = linkEl ? linkEl.href : '';

            if (title) {
                items.push({title, publish_date, category, summary, url});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = WhitehouseBriefingItem()
        item.title = d.get("title", "")
        item.publish_date = d.get("publish_date", "")
        item.category = d.get("category", "")
        item.summary = d.get("summary", "")
        item.url = d.get("url", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Briefing {i}:")
        print(f"    Title:    {item.title}")
        print(f"    Date:     {item.publish_date}")
        print(f"    Category: {item.category}")
        print(f"    Summary:  {item.summary[:100]}...")
        print(f"    URL:      {item.url}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("whitehouse")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = WhitehouseSearchRequest()
            result = whitehouse_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} briefings")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
