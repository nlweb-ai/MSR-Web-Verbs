"""
Auto-generated Playwright script (Python)
Car and Driver – Search Articles
Query: "best SUV 2025"

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class SearchRequest:
    search_query: str = "best SUV 2025"
    max_results: int = 5


@dataclass
class Article:
    title: str = ""
    url: str = ""
    description: str = ""
    date: str = ""


@dataclass
class SearchResult:
    articles: List[Article] = field(default_factory=list)


def caranddriver_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search Car and Driver for articles/reviews."""
    print(f"  Query: {request.search_query}\n")

    # ── Navigate to search results ────────────────────────────────────
    query = quote_plus(request.search_query)
    url = f"https://www.caranddriver.com/search/?q={query}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Car and Driver search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = SearchResult()

    # ── Extract articles from search results ──────────────────────────
    checkpoint("Extract search results")
    js_code = r"""(maxResults) => {
        const results = [];
        const links = document.querySelectorAll('a[data-id="search-content-preview-link"]');
        for (const a of links) {
            const href = a.getAttribute('href') || '';
            const img = a.querySelector('img');
            const title = img ? (img.getAttribute('alt') || '').trim() : '';
            // Description: get all text, remove the title and date to isolate snippet
            const allText = (a.textContent || '').trim();
            const dateMatch = allText.match(/([A-Z][a-z]{2,8}\s+\d{1,2},\s+\d{4})/);
            const date = dateMatch ? dateMatch[1] : '';
            // Description is the text between title and date
            let description = allText;
            if (title) description = description.replace(title, '').trim();
            if (date) description = description.replace(date, '').trim();

            if (title && title.length > 5) {
                results.push({
                    title,
                    url: href.startsWith('http') ? href : 'https://www.caranddriver.com' + href,
                    description,
                    date
                });
            }
            if (results.length >= maxResults) break;
        }
        return results;
    }"""
    articles_data = page.evaluate(js_code, request.max_results)

    for ad in articles_data:
        article = Article()
        article.title = ad.get("title", "")
        article.url = ad.get("url", "")
        article.description = ad.get("description", "")
        article.date = ad.get("date", "")
        result.articles.append(article)

    # ── Print results ─────────────────────────────────────────────────
    for i, a in enumerate(result.articles, 1):
        print(f"\n  Article {i}:")
        print(f"    Title:       {a.title}")
        print(f"    URL:         {a.url}")
        print(f"    Description: {a.description[:100]}")
        print(f"    Date:        {a.date}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("caranddriver")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = caranddriver_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
