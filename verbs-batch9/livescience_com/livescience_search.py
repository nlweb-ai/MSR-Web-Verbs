"""
Playwright script (Python) — Live Science Article Search
Search Live Science for articles and extract details.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class LiveScienceRequest:
    search_query: str = "black holes"
    max_results: int = 5


@dataclass
class ArticleItem:
    title: str = ""
    author: str = ""
    date: str = ""
    summary: str = ""


@dataclass
class LiveScienceResult:
    query: str = ""
    articles: List[ArticleItem] = field(default_factory=list)


# Searches Live Science for articles matching the query and returns
# up to max_results articles with title, author, date, and summary.
def search_livescience_articles(page: Page, request: LiveScienceRequest) -> LiveScienceResult:
    import urllib.parse
    url = f"https://www.livescience.com/search?searchTerm={urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Live Science search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = LiveScienceResult(query=request.search_query)

    checkpoint("Extract article listings")
    js_code = """(max) => {
        const results = [];
        const cards = document.querySelectorAll('div.listingResult');
        const seen = new Set();
        for (const card of cards) {
            if (results.length >= max) break;
            const text = card.innerText.trim();
            const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            if (lines.length < 2) continue;
            const title = lines[0];
            if (!title || title.length < 10 || seen.has(title)) continue;
            seen.add(title);
            let author = '', date = '', summary = '';
            // Line 1 should be "By Author published Date"
            const byLine = lines[1] || '';
            const m = byLine.match(/^By\\s+(.+?)\\s+published\\s+(.+)$/i);
            if (m) { author = m[1]; date = m[2]; }
            // Lines after byline are summary
            if (lines.length > 2) summary = lines.slice(2).join(' ').substring(0, 200);
            results.push({ title, author, date, summary });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ArticleItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.date = d.get("date", "")
        item.summary = d.get("summary", "")
        result.articles.append(item)

    print(f"\nFound {len(result.articles)} articles for '{request.search_query}':")
    for i, item in enumerate(result.articles, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Author: {item.author}  Date: {item.date}")
        print(f"     Summary: {item.summary[:80]}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("livescience")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_livescience_articles(page, LiveScienceRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
