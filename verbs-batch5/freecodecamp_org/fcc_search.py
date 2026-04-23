"""
Auto-generated Playwright script (Python)
freecodecamp.org – Tutorial Search
Query: Python web scraping

Generated on: 2026-04-18T01:00:14.063Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import os, sys, shutil, urllib.parse
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class FCCSearchRequest:
    search_query: str = "Python web scraping"
    max_results: int = 5


@dataclass(frozen=True)
class FCCArticle:
    title: str = ""
    author: str = ""
    publication_date: str = ""
    tags: str = ""


@dataclass(frozen=True)
class FCCSearchResult:
    articles: list = None  # list[FCCArticle]


def fcc_search(page: Page, request: FCCSearchRequest) -> FCCSearchResult:
    """Search freeCodeCamp news for tutorials."""
    query = request.search_query
    max_results = request.max_results
    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    # ── Navigate to search ────────────────────────────────────────────
    url = f"https://www.freecodecamp.org/news/search/?query={urllib.parse.quote_plus(query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to freeCodeCamp search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    print(f"  Loaded: {page.url}")

    # ── Extract articles ──────────────────────────────────────────────
    checkpoint("Extract article listings")
    results_data = page.evaluate(r"""(maxResults) => {
        const cards = document.querySelectorAll('article.post-card');
        const results = [];
        for (const card of cards) {
            if (results.length >= maxResults) break;
            const titleEl = card.querySelector('h2.post-card-title');
            const authorEl = card.querySelector('a.meta-item');
            const dateEl = card.querySelector('time.meta-item');
            const tagsEl = card.querySelector('span.post-card-tags');
            if (!titleEl) continue;
            results.push({
                title: titleEl.textContent.trim(),
                author: authorEl ? authorEl.textContent.trim() : '',
                date: dateEl ? dateEl.textContent.trim() : '',
                tags: tagsEl ? tagsEl.textContent.trim() : ''
            });
        }
        return results;
    }""", max_results)

    articles = []
    for r in results_data:
        articles.append(FCCArticle(
            title=r.get("title", ""),
            author=r.get("author", ""),
            publication_date=r.get("date", ""),
            tags=r.get("tags", ""),
        ))

    # ── Print results ─────────────────────────────────────────────────
    print("=" * 60)
    print(f'freeCodeCamp - "{query}" Tutorials')
    print("=" * 60)
    for idx, a in enumerate(articles, 1):
        print(f"\n{idx}. {a.title}")
        print(f"   Author: {a.author} | Date: {a.publication_date}")
        if a.tags:
            print(f"   Tags: {a.tags}")

    print(f"\nFound {len(articles)} articles")
    return FCCSearchResult(articles=articles)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("freecodecamp_org")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = fcc_search(page, FCCSearchRequest())
            print(f"\nReturned {len(result.articles or [])} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
