"""
Auto-generated Playwright script (Python)
Family Handyman – Search articles

Uses CDP-launched Chrome to avoid bot detection.
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
class SearchRequest:
    search_query: str = "plumbing repair guide"
    max_results: int = 5


@dataclass
class Article:
    title: str = ""
    url: str = ""
    summary: str = ""


@dataclass
class SearchResult:
    articles: List[Article] = field(default_factory=list)


def familyhandyman_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search Family Handyman and extract article results."""
    print(f"  Query: {request.search_query}\n")

    encoded = quote_plus(request.search_query)
    url = f"https://www.familyhandyman.com/?s={encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Family Handyman search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = SearchResult()

    checkpoint("Extract search results")
    articles_data = page.evaluate(
        r"""(max) => {
            const cards = document.querySelectorAll('article');
            const items = [];
            for (let i = 0; i < cards.length && items.length < max; i++) {
                const card = cards[i];
                const link = card.querySelector('a.post-thumbnail, a[data-name]');
                const summaryEl = card.querySelector('.content-text p, .content-text, p');

                const title = (link && link.getAttribute('data-name')) || '';
                const url = link ? link.href : '';
                const summary = summaryEl ? summaryEl.textContent.trim() : '';

                if (title && title.length > 5) {
                    items.push({title, url, summary: summary.slice(0, 300)});
                }
            }
            return items;
        }""",
        request.max_results,
    )

    for d in articles_data:
        article = Article()
        article.title = d.get("title", "")
        article.url = d.get("url", "")
        article.summary = d.get("summary", "")
        result.articles.append(article)

    for i, a in enumerate(result.articles, 1):
        print(f"\n  Article {i}:")
        print(f"    Title:   {a.title}")
        print(f"    URL:     {a.url}")
        print(f"    Summary: {a.summary}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("familyhandyman")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = familyhandyman_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
