"""
Auto-generated Playwright script (Python)
Condé Nast Traveler – Search for travel articles by keyword
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CntravelerSearchRequest:
    search_query: str = "best beaches"
    max_results: int = 5


@dataclass
class CntravelerArticleItem:
    title: str = ""
    author: str = ""
    publish_date: str = ""
    category: str = ""
    summary: str = ""
    image_url: str = ""


@dataclass
class CntravelerSearchResult:
    items: List[CntravelerArticleItem] = field(default_factory=list)


# Search for travel articles on Condé Nast Traveler by keyword.
def cntraveler_search(page: Page, request: CntravelerSearchRequest) -> CntravelerSearchResult:
    """Search for travel articles on Condé Nast Traveler."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://www.cntraveler.com/search?q={query}"
    print(f"Loading {url}...")
    checkpoint("Navigate to CN Traveler search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = CntravelerSearchResult()

    checkpoint("Extract article listings")
    js_code = """(max) => {
        const cards = document.querySelectorAll('article, [class*="SearchResult"], [class*="summary-item"], [class*="Card"], [class*="card"], [data-testid*="search"]');
        const items = [];
        for (const card of cards) {
            if (items.length >= max) break;
            const titleEl = card.querySelector('h2, h3, h4, [class*="title"], [class*="headline"] a');
            const authorEl = card.querySelector('[class*="author"], [class*="byline"], [rel="author"]');
            const dateEl = card.querySelector('time, [class*="date"], [class*="time"]');
            const categoryEl = card.querySelector('[class*="category"], [class*="rubric"], [class*="label"], [class*="tag"]');
            const summaryEl = card.querySelector('p, [class*="description"], [class*="summary"], [class*="dek"]');
            const imgEl = card.querySelector('img');

            const title = titleEl ? titleEl.textContent.trim() : '';
            const author = authorEl ? authorEl.textContent.trim() : '';
            const publish_date = dateEl ? (dateEl.getAttribute('datetime') || dateEl.textContent.trim()) : '';
            const category = categoryEl ? categoryEl.textContent.trim() : '';
            const summary = summaryEl ? summaryEl.textContent.trim() : '';
            const image_url = imgEl ? (imgEl.getAttribute('src') || imgEl.getAttribute('data-src') || '') : '';

            if (title) {
                items.push({title, author, publish_date, category, summary, image_url});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = CntravelerArticleItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.publish_date = d.get("publish_date", "")
        item.category = d.get("category", "")
        item.summary = d.get("summary", "")
        item.image_url = d.get("image_url", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Article {i}:")
        print(f"    Title:     {item.title}")
        print(f"    Author:    {item.author}")
        print(f"    Date:      {item.publish_date}")
        print(f"    Category:  {item.category}")
        print(f"    Summary:   {item.summary[:100]}...")
        print(f"    Image:     {item.image_url[:80]}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("cntraveler")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = CntravelerSearchRequest()
            result = cntraveler_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
