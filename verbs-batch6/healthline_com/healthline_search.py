"""
Auto-generated Playwright script (Python)
Healthline – Health Articles Search
Query: "intermittent fasting benefits"

Generated on: 2026-04-18T05:33:32.356Z
Recorded 2 browser interactions
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
    query: str = "intermittent fasting benefits"
    max_results: int = 5


@dataclass
class Article:
    title: str = ""
    author: str = ""
    date: str = ""
    summary: str = ""


@dataclass
class ArticleResult:
    articles: List[Article] = field(default_factory=list)


def healthline_search(page: Page, request: ArticleRequest) -> ArticleResult:
    """Search Healthline for health articles."""
    print(f"  Query: {request.query}\n")

    from urllib.parse import quote_plus
    # Healthline search results are hard to separate from nav links, use Google site search
    url = f"https://www.google.com/search?q=site%3Ahealthline.com+{quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Google site search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract search results")
    articles_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();

        // Google result headings (h3)
        const h3s = document.querySelectorAll('h3');
        for (const h of h3s) {
            if (results.length >= maxResults) break;
            let title = h.innerText.trim();
            title = title.replace(/\s*[\|–—-]\s*Healthline.*$/i, '').trim();
            if (!title || title.length < 10 || seen.has(title)) continue;
            if (/^(search|sign|log|menu|home|all|images|videos|news|more|tools)/i.test(title)) continue;
            seen.add(title);

            let author = '', date = '', summary = '';
            const container = h.closest('[data-snhf]') || h.closest('[class*="g"]') || h.parentElement?.parentElement;
            if (container) {
                const text = container.innerText || '';
                const byM = text.match(/by\s+([A-Z][^\n,]{3,40})/i);
                if (byM) author = byM[1].trim();
                const dateM = text.match(/((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s*\d{4})/i);
                if (dateM) date = dateM[1];
                const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 30 && l !== title);
                if (lines.length > 0) summary = lines[0];
            }

            results.push({ title: title.slice(0, 120), author: author.slice(0, 60), date, summary: summary.slice(0, 200) });
        }
        return results;
    }""", request.max_results)

    articles = [Article(**d) for d in articles_data]

    result = ArticleResult(articles=articles[:request.max_results])

    print("\n" + "=" * 60)
    print(f"Healthline: {request.query}")
    print("=" * 60)
    for i, a in enumerate(result.articles, 1):
        print(f"  {i}. {a.title}")
        if a.author:
            print(f"     Author: {a.author}")
        if a.date:
            print(f"     Date:   {a.date}")
        if a.summary:
            print(f"     {a.summary[:80]}...")
    print(f"\nTotal: {len(result.articles)} articles")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("healthline_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = healthline_search(page, ArticleRequest())
            print(f"\nReturned {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
