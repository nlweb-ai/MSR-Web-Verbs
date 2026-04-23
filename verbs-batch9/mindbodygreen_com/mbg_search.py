"""
Playwright script (Python) — MindBodyGreen Article Search
Search mindbodygreen for wellness articles.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MBGRequest:
    query: str = "gut health"
    max_results: int = 5


@dataclass
class ArticleItem:
    title: str = ""
    author: str = ""
    date: str = ""
    category: str = ""
    summary: str = ""


@dataclass
class MBGResult:
    articles: List[ArticleItem] = field(default_factory=list)


# Searches mindbodygreen for wellness articles and extracts title,
# author, publish date, category, and summary.
def search_mbg(page: Page, request: MBGRequest) -> MBGResult:
    url = f"https://www.mindbodygreen.com/search?q={request.query.replace(' ', '+')}"
    print(f"Loading {url}...")
    checkpoint("Navigate to MBG search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = MBGResult()

    checkpoint("Extract articles from search results")
    js_code = """(max) => {
        const results = [];
        const lines = document.body.innerText.split('\\n').map(l => l.trim()).filter(l => l);
        // Find "TOP 100 RESULTS FOR" marker
        let start = lines.findIndex(l => l.startsWith('TOP') && l.includes('RESULTS FOR'));
        if (start < 0) return results;
        start++;
        // Pattern: CATEGORY, Title, Summary, #tags..., AUTHOR, Date
        let i = start;
        while (i < lines.length && results.length < max) {
            // Current line should be CATEGORY (all caps, no #)
            if (lines[i] === lines[i].toUpperCase() && !lines[i].startsWith('#') && lines[i].length > 3) {
                const category = lines[i];
                const title = (i + 1 < lines.length) ? lines[i + 1] : '';
                const summary = (i + 2 < lines.length && !lines[i + 2].startsWith('#')) ? lines[i + 2] : '';
                // Skip past tags to find author and date
                let j = i + 2;
                // Skip summary line if present
                if (j < lines.length && !lines[j].startsWith('#')) j++;
                // Skip # tags
                while (j < lines.length && lines[j].startsWith('#')) j++;
                const author = (j < lines.length) ? lines[j] : '';
                const date = (j + 1 < lines.length) ? lines[j + 1] : '';
                if (title.length >= 10) {
                    results.push({ title, author, date, category, summary });
                }
                i = j + 2;
            } else {
                i++;
            }
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ArticleItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.date = d.get("date", "")
        item.category = d.get("category", "")
        item.summary = d.get("summary", "")
        result.articles.append(item)

    print(f"\nFound {len(result.articles)} articles:")
    for i, a in enumerate(result.articles, 1):
        print(f"\n  {i}. {a.title}")
        print(f"     Author: {a.author}  Date: {a.date}")
        print(f"     Category: {a.category}")
        print(f"     Summary: {a.summary}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("mbg")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_mbg(page, MBGRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
