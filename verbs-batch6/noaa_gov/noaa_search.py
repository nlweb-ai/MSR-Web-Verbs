"""
Auto-generated Playwright script (Python)
NOAA – Weather/Climate Search
Query: "hurricane season forecast 2024"
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ArticleRequest:
    query: str = "hurricane season forecast 2024"
    max_results: int = 5


@dataclass
class Article:
    title: str = ""
    description: str = ""
    url: str = ""


@dataclass
class ArticleResult:
    articles: List[Article] = field(default_factory=list)


def noaa_search(page: Page, request: ArticleRequest) -> ArticleResult:
    """Search NOAA for weather/climate articles via Google site search."""
    print(f"  Query: {request.query}\n")

    from urllib.parse import quote_plus
    url = f"https://www.google.com/search?q=site%3Anoaa.gov+{quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Google site search for NOAA")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    checkpoint("Extract article listings from Google results")
    articles_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();
        const h3s = document.querySelectorAll('h3');
        for (const h of h3s) {
            if (results.length >= maxResults) break;
            let text = h.innerText.trim();
            text = text.replace(/\s*[\|\u2013\u2014-]\s*NOAA.*$/i, '').trim();
            if (text.length < 5 || seen.has(text)) continue;
            seen.add(text);

            let url = '';
            const link = h.closest('a') || h.parentElement?.closest('a');
            if (link) url = link.href || '';

            results.push({ title: text.slice(0, 150), description: '', url });
        }
        return results;
    }""", request.max_results)

    articles = [Article(**d) for d in articles_data]
    result = ArticleResult(articles=articles[:request.max_results])

    print("\n" + "=" * 60)
    print(f"NOAA: {request.query}")
    print("=" * 60)
    for i, a in enumerate(result.articles, 1):
        print(f"  {i}. {a.title}")
        if a.description:
            print(f"     {a.description[:100]}...")
        if a.url:
            print(f"     URL: {a.url}")
    print(f"\nTotal: {len(result.articles)} articles")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("noaa_gov")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = noaa_search(page, ArticleRequest())
            print(f"\nReturned {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
