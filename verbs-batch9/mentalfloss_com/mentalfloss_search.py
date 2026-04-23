"""
Playwright script (Python) — Mental Floss Article Search
Search Mental Floss for articles and extract details.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MentalFlossRequest:
    query: str = "fascinating facts"
    max_results: int = 5


@dataclass
class ArticleItem:
    title: str = ""
    author: str = ""
    date: str = ""
    category: str = ""


@dataclass
class MentalFlossResult:
    articles: List[ArticleItem] = field(default_factory=list)


# Searches Mental Floss for articles and extracts title,
# author, publish date, and summary.
def search_mentalfloss(page: Page, request: MentalFlossRequest) -> MentalFlossResult:
    url = f"https://www.mentalfloss.com/search?q={request.query.replace(' ', '+')}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Mental Floss search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = MentalFlossResult()

    checkpoint("Extract articles from search results")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        const articles = document.querySelectorAll('article');
        for (const art of articles) {
            if (results.length >= max) break;
            const lines = art.innerText.split('\\n').map(l => l.trim()).filter(l => l && l !== '|');
            if (lines.length < 2) continue;
            const category = lines[0];
            const title = lines[1];
            if (!title || title.length < 10) continue;
            if (seen.has(title)) continue;
            seen.add(title);
            const author = lines.length > 2 ? lines[2] : '';
            const date = lines.length > 3 ? lines[3] : '';
            results.push({ title, author, date, category });
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
        result.articles.append(item)

    print(f"\nFound {len(result.articles)} articles:")
    for i, a in enumerate(result.articles, 1):
        print(f"\n  {i}. {a.title}")
        print(f"     Author: {a.author}  Date: {a.date}")
        print(f"     Category: {a.category}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("mentalfloss")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_mentalfloss(page, MentalFlossRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
