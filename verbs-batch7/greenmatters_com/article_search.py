"""
Auto-generated Playwright script (Python)
Green Matters – Browse sustainable living articles

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
class ArticleSearchRequest:
    topic: str = "what-is-sustainable-living"
    max_results: int = 5


@dataclass
class Article:
    title: str = ""
    author: str = ""
    date: str = ""
    summary: str = ""


@dataclass
class ArticleSearchResult:
    articles: List[Article] = field(default_factory=list)


def article_search(page: Page, request: ArticleSearchRequest) -> ArticleSearchResult:
    """Browse Green Matters topic page and extract articles."""
    print(f"  Topic: {request.topic}")
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Navigate to topic page")
    page.goto(f"https://www.greenmatters.com/t/{request.topic}", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract article cards")
    result = ArticleSearchResult()

    items = page.evaluate(
        r"""(max) => {
            const articles = document.querySelectorAll('article');
            const results = [];
            for (let i = 0; i < articles.length && results.length < max; i++) {
                const a = articles[i];

                // Title from h2 span
                const h2 = a.querySelector('h2 span');
                const title = h2 ? h2.textContent.trim() : '';
                if (!title || title.length < 5) continue;

                // Summary from doc-excerpt
                const excerptEl = a.querySelector('[class*="doc-excerpt"]');
                const summary = excerptEl ? excerptEl.textContent.trim() : '';

                // Author from footer span span
                const authorEl = a.querySelector('footer span span');
                const author = authorEl ? authorEl.textContent.trim() : '';

                // Date from footer time element
                const timeEl = a.querySelector('footer time');
                const date = timeEl ? timeEl.getAttribute('datetime') : '';

                results.push({title, author, date, summary});
            }
            return results;
        }""",
        request.max_results,
    )

    for item in items:
        a = Article()
        a.title = item.get("title", "")
        a.author = item.get("author", "")
        a.date = item.get("date", "")
        a.summary = item.get("summary", "")
        result.articles.append(a)

    for i, a in enumerate(result.articles):
        print(f"  Article {i + 1}:")
        print(f"    Title:   {a.title}")
        print(f"    Author:  {a.author}")
        print(f"    Date:    {a.date}")
        print(f"    Summary: {a.summary[:120]}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("greenmatters")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = ArticleSearchRequest()
            result = article_search(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
