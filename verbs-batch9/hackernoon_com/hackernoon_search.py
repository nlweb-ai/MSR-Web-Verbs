"""
Playwright script (Python) — HackerNoon Article Search
Search HackerNoon for tech articles.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class HackerNoonRequest:
    search_query: str = "blockchain development"
    max_results: int = 5


@dataclass
class ArticleItem:
    title: str = ""
    author: str = ""
    description: str = ""


@dataclass
class HackerNoonResult:
    query: str = ""
    items: List[ArticleItem] = field(default_factory=list)


# Searches HackerNoon for articles matching the query and returns
# up to max_results articles with title, author, and description.
def search_hackernoon(page: Page, request: HackerNoonRequest) -> HackerNoonResult:
    import urllib.parse
    url = f"https://hackernoon.com/search?query={urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = HackerNoonResult(query=request.search_query)

    checkpoint("Extract article listings")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        const lines = document.body.innerText.split('\\n').filter(l => l.trim());
        for (let i = 0; i < lines.length; i++) {
            if (results.length >= max) break;
            if (lines[i].trim() !== 'BLOG') continue;
            const title = (lines[i+1] || '').trim();
            if (!title || title.length < 10 || seen.has(title)) continue;
            seen.add(title);
            const description = (lines[i+2] || '').trim();
            let author = '';
            const byLine = (lines[i+3] || '').trim();
            if (byLine.startsWith('by @')) author = byLine.substring(4);
            else if (byLine.startsWith('by ')) author = byLine.substring(3);
            results.push({title, description, author});
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ArticleItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.description = d.get("description", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} articles for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Author: {item.author}")
        print(f"     {item.description[:100]}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("hackernoon")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_hackernoon(page, HackerNoonRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
