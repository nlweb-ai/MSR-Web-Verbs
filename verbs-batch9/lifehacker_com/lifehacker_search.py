"""
Playwright script (Python) — Lifehacker Article Search
Browse Lifehacker and extract recent articles with details.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class LifehackerRequest:
    search_query: str = "productivity tips"
    max_results: int = 5


@dataclass
class ArticleItem:
    title: str = ""
    date: str = ""


@dataclass
class LifehackerResult:
    query: str = ""
    articles: List[ArticleItem] = field(default_factory=list)


# Browses Lifehacker homepage and extracts recent articles
# with title and publish date.
def search_lifehacker_articles(page: Page, request: LifehackerRequest) -> LifehackerResult:
    url = "https://lifehacker.com"
    print(f"Loading {url}...")
    checkpoint("Navigate to Lifehacker")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)

    result = LifehackerResult(query=request.search_query)

    checkpoint("Extract article listings")
    js_code = """(max) => {
        const results = [];
        // Get page text - articles appear as: CATEGORY\\nTitle\\nAuthor or CATEGORY\\nTitle\\nDate
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        
        // Find date lines and work backwards to find title
        const dateRe = /^\\s*(January|February|March|April|May|June|July|August|September|October|November|December)\\s+\\d{1,2},\\s+\\d{4}/;
        const seen = new Set();
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (dateRe.test(lines[i])) {
                const date = lines[i].trim();
                // Walk backwards to find title (skip category which is ALL CAPS)
                let title = '';
                let author = '';
                let category = '';
                for (let j = i - 1; j >= Math.max(0, i - 4); j--) {
                    const line = lines[j];
                    if (line === line.toUpperCase() && line.length < 30) {
                        category = line;
                        break;
                    }
                    if (!title && line.length > 15) title = line;
                    else if (title && !author && line.length > 2 && line.length < 40) author = line;
                }
                if (title && !seen.has(title)) {
                    seen.add(title);
                    results.push({ title, date });
                }
            }
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ArticleItem()
        item.title = d.get("title", "")
        item.date = d.get("date", "")
        result.articles.append(item)

    print(f"\nFound {len(result.articles)} articles:")
    for i, item in enumerate(result.articles, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Date: {item.date}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("lifehacker")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_lifehacker_articles(page, LifehackerRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
