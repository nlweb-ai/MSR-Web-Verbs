"""
Playwright script (Python) — HubSpot Blog Search
Search HubSpot blog for marketing articles.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class HubSpotSearchRequest:
    search_query: str = "email marketing"
    max_results: int = 5


@dataclass
class ArticleItem:
    title: str = ""
    author: str = ""
    publish_date: str = ""
    category: str = ""
    read_time: str = ""


@dataclass
class HubSpotSearchResult:
    query: str = ""
    items: List[ArticleItem] = field(default_factory=list)


def search_hubspot_blog(page: Page, request: HubSpotSearchRequest) -> HubSpotSearchResult:
    import urllib.parse
    url = f"https://blog.hubspot.com/search?query={urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = HubSpotSearchResult(query=request.search_query)

    checkpoint("Extract article listings")
    js_code = """(max) => {
        const results = [];
        const cards = document.querySelectorAll('article, [class*="blog-post"], [class*="post-listing"], [class*="search-result"], [class*="card"]');
        for (const card of cards) {
            if (results.length >= max) break;
            const titleEl = card.querySelector('h2, h3, a[class*="title"], [class*="post-title"]');
            const title = titleEl ? titleEl.textContent.trim() : '';
            if (!title || title.length < 10) continue;
            if (results.some(r => r.title === title)) continue;

            let author = '';
            const authorEl = card.querySelector('[class*="author"], [class*="byline"]');
            if (authorEl) author = authorEl.textContent.trim().replace(/^by\\s*/i, '');

            let publishDate = '';
            const dateEl = card.querySelector('time, [class*="date"], [datetime]');
            if (dateEl) publishDate = dateEl.textContent.trim() || dateEl.getAttribute('datetime') || '';

            let category = '';
            const catEl = card.querySelector('[class*="category"], [class*="topic"], [class*="tag"]');
            if (catEl) category = catEl.textContent.trim();

            let readTime = '';
            const text = (card.textContent || '').replace(/\\s+/g, ' ');
            const readMatch = text.match(/(\\d+)\\s*min\\s*read/i);
            if (readMatch) readTime = readMatch[1] + ' min read';

            results.push({ title, author, publish_date: publishDate, category, read_time: readTime });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ArticleItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.publish_date = d.get("publish_date", "")
        item.category = d.get("category", "")
        item.read_time = d.get("read_time", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} articles for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Author: {item.author}  Date: {item.publish_date}")
        print(f"     Category: {item.category}  Read time: {item.read_time}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("hubspot")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_hubspot_blog(page, HubSpotSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
