"""
Auto-generated Playwright script (Python)
MotorTrend – Car Comparison Search
Query: "SUV comparison 2024"
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
    query: str = "SUV comparison 2024"
    max_results: int = 5


@dataclass
class Article:
    title: str = ""
    vehicles: str = ""
    url: str = ""


@dataclass
class ArticleResult:
    articles: List[Article] = field(default_factory=list)


def motortrend_search(page: Page, request: ArticleRequest) -> ArticleResult:
    """Search MotorTrend for car comparison articles."""
    print(f"  Query: {request.query}\n")

    from urllib.parse import quote_plus
    url = f"https://www.google.com/search?q=site%3Amotortrend.com+{quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Google site search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract search results")
    articles_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();

        const h3s = document.querySelectorAll('h3');
        for (const h of h3s) {
            if (results.length >= maxResults) break;
            let title = h.innerText.trim();
            title = title.replace(/\s*[\|–—-]\s*MotorTrend.*$/i, '').trim();
            if (!title || title.length < 10 || seen.has(title)) continue;
            if (/^(search|sign|log|menu|home|all|images|videos|news|more|tools)/i.test(title)) continue;
            seen.add(title);

            let vehicles = '', articleUrl = '';
            const container = h.closest('[data-snhf]') || h.closest('[class*="g"]') || h.parentElement?.parentElement;
            if (container) {
                const a = container.querySelector('a');
                if (a) articleUrl = a.getAttribute('href') || '';
                const text = container.innerText || '';
                const vm = text.match(/((?:[A-Z][a-z]+\s+){1,3}(?:vs\.?|versus)\s+(?:[A-Z][a-z]+\s+){1,3})/i);
                if (vm) vehicles = vm[1].trim();
            }

            results.push({ title: title.slice(0, 120), vehicles: vehicles.slice(0, 80), url: articleUrl });
        }
        return results;
    }""", request.max_results)

    articles = [Article(**d) for d in articles_data]

    result = ArticleResult(articles=articles[:request.max_results])

    print("\n" + "=" * 60)
    print(f"MotorTrend: {request.query}")
    print("=" * 60)
    for i, a in enumerate(result.articles, 1):
        print(f"  {i}. {a.title}")
        if a.vehicles:
            print(f"     Vehicles: {a.vehicles}")
        if a.url:
            print(f"     URL:      {a.url}")
    print(f"\nTotal: {len(result.articles)} articles")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("motortrend_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = motortrend_search(page, ArticleRequest())
            print(f"\nReturned {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
