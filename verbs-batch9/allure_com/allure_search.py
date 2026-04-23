"""
Playwright script (Python) — Allure Article Search
Search for beauty articles and extract details.
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
class AllureSearchRequest:
    search_query: str = "best sunscreens"
    max_results: int = 5


@dataclass
class ArticleItem:
    title: str = ""
    author: str = ""
    publish_date: str = ""
    summary: str = ""


@dataclass
class AllureSearchResult:
    query: str = ""
    items: List[ArticleItem] = field(default_factory=list)


# Searches Allure for beauty/lifestyle articles.
def search_allure(page: Page, request: AllureSearchRequest) -> AllureSearchResult:
    """Search Allure for articles."""
    encoded = quote_plus(request.search_query)
    url = f"https://www.allure.com/search?q={encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Allure search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = AllureSearchResult(query=request.search_query)

    checkpoint("Extract articles")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('[class*="summary-item"], [class*="SearchResultItem"], article, [data-testid*="search-result"]');
        let candidates = Array.from(cards).filter(c => c.textContent.length > 30);
        candidates = candidates.filter(c => !candidates.some(o => o !== c && o.contains(c)));
        for (const card of candidates) {
            if (items.length >= max) break;
            const text = (card.textContent || '').replace(/\\s+/g, ' ').trim();

            let title = '';
            const titleEl = card.querySelector('h2 a, h3 a, h2, h3, [class*="title"], [class*="hed"]');
            if (titleEl) title = titleEl.textContent.trim();

            let author = '';
            let date = '';
            const lines = card.innerText.split('\\n').map(l => l.trim());
            for (const line of lines) {
                if (!author) {
                    const am = line.match(/^BY\\s+(.+)/i);
                    if (am) author = am[1].trim();
                }
                if (!date) {
                    const dm = line.match(/^((?:January|February|March|April|May|June|July|August|September|October|November|December)\\s+\\d{1,2},\\s*\\d{4})/i);
                    if (dm) date = dm[1];
                }
            }

            let summary = '';
            const sumEl = card.querySelector('p, [class*="dek"], [class*="description"]');
            if (sumEl) summary = sumEl.textContent.trim().substring(0, 200);

            if (title) items.push({title, author, publish_date: date, summary});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ArticleItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.publish_date = d.get("publish_date", "")
        item.summary = d.get("summary", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} articles for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Author: {item.author}")
        print(f"     Date:   {item.publish_date}")
        print(f"     Summary: {item.summary[:100]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("allure")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_allure(page, AllureSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
