"""
Playwright script (Python) — Everyday Health Article Search
Search for health articles on EverydayHealth.com.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class EverydayHealthSearchRequest:
    search_query: str = "arthritis management"
    max_results: int = 5


@dataclass
class HealthArticleItem:
    title: str = ""
    publish_date: str = ""
    summary: str = ""


@dataclass
class EverydayHealthSearchResult:
    query: str = ""
    items: List[HealthArticleItem] = field(default_factory=list)


# Searches EverydayHealth.com for articles matching the query and returns
# up to max_results articles with title, author, medical reviewer, publish date, and summary.
def search_everydayhealth_articles(page: Page, request: EverydayHealthSearchRequest) -> EverydayHealthSearchResult:
    import urllib.parse
    url = f"https://www.everydayhealth.com/search/?q={urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = EverydayHealthSearchResult(query=request.search_query)

    checkpoint("Extract article listings")
    js_code = """(max) => {
        const results = [];
        const cards = document.querySelectorAll('article, [class*="result"], [class*="card"], .search-result');
        for (const card of cards) {
            if (results.length >= max) break;
            const titleEl = card.querySelector('h2, h3, h4, a[class*="title"], [class*="headline"]');
            const title = titleEl ? titleEl.textContent.trim() : '';
            if (!title || title.length < 10) continue;
            if (results.some(r => r.title === title)) continue;

            const text = (card.textContent || '').replace(/\\s+/g, ' ').trim();

            let author = '';
            const authorEl = card.querySelector('[class*="author"], [class*="byline"], [rel="author"]');
            if (authorEl) author = authorEl.textContent.trim().replace(/^by\\s*/i, '');

            let reviewer = '';
            const revMatch = text.match(/(?:reviewed|medically reviewed)\\s+by\\s+([^,\\n]+)/i);
            if (revMatch) reviewer = revMatch[1].trim();

            let date = '';
            const dateEl = card.querySelector('time, [class*="date"], [datetime]');
            if (dateEl) date = (dateEl.getAttribute('datetime') || dateEl.textContent || '').trim();

            let summary = '';
            const descEl = card.querySelector('p, [class*="description"], [class*="summary"], [class*="excerpt"]');
            if (descEl) summary = descEl.textContent.trim().substring(0, 200);

            results.push({ title, author, medical_reviewer: reviewer, publish_date: date, summary });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = HealthArticleItem()
        item.title = d.get("title", "")
        item.publish_date = d.get("publish_date", "")
        item.summary = d.get("summary", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} articles for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Date: {item.publish_date}")
        print(f"     Summary: {item.summary[:100]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("everydayhealth")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_everydayhealth_articles(page, EverydayHealthSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
