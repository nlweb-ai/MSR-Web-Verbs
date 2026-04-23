"""
Auto-generated Playwright script (Python)
Better Homes & Gardens – Article Search
Query: "small bathroom remodel"

Generated on: 2026-04-18T04:57:29.700Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ArticleRequest:
    query: str = "small bathroom remodel"
    max_articles: int = 5


@dataclass
class Article:
    title: str = ""
    description: str = ""
    url: str = ""


@dataclass
class ArticleResult:
    articles: list = field(default_factory=list)


def bhg_search(page: Page, request: ArticleRequest) -> ArticleResult:
    """Search Better Homes & Gardens for articles."""
    print(f"  Query: {request.query}\n")

    url = f"https://www.bhg.com/search?q={quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to BHG search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract article listings")
    articles_data = page.evaluate(r"""(maxArticles) => {
        const results = [];
        const cards = document.querySelectorAll(
            'article, .card, [class*="Card"], [class*="search-result"], a[href*="/"]'
        );
        const seen = new Set();
        for (const card of cards) {
            if (results.length >= maxArticles) break;
            const titleEl = card.querySelector('h2, h3, h4, .title, [class*="title"]');
            const title = titleEl ? titleEl.innerText.trim() : '';
            if (!title || title.length < 5 || seen.has(title)) continue;
            seen.add(title);

            const descEl = card.querySelector('p, .description, [class*="desc"]');
            const description = descEl ? descEl.innerText.trim().slice(0, 200) : '';

            const linkEl = card.tagName === 'A' ? card : card.querySelector('a');
            const url = linkEl ? linkEl.href : '';

            results.push({ title, description, url });
        }
        return results;
    }""", request.max_articles)

    result = ArticleResult(articles=[Article(**a) for a in articles_data])

    print("\n" + "=" * 60)
    print(f"BHG: {request.query}")
    print("=" * 60)
    for a in result.articles:
        print(f"  {a.title}")
        print(f"    Description: {a.description[:80]}...")
        print(f"    URL: {a.url}")
    print(f"\n  Total: {len(result.articles)} articles")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("bhg_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = bhg_search(page, ArticleRequest())
            print(f"\nReturned {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
