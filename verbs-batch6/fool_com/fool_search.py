"""
Auto-generated Playwright script (Python)
Motley Fool – Article Search
Query: "dividend stocks 2025"

Generated on: 2026-04-18T05:24:26.657Z
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
    query: str = "dividend stocks 2025"
    max_results: int = 5


@dataclass
class Article:
    headline: str = ""
    author: str = ""
    date: str = ""
    summary: str = ""


@dataclass
class ArticleResult:
    articles: list = field(default_factory=list)


def fool_search(page: Page, request: ArticleRequest) -> ArticleResult:
    """Search Motley Fool for articles."""
    print(f"  Query: {request.query}\n")

    # Navigate to Google with site:fool.com search
    url = f"https://www.google.com/search?q=site:fool.com+{quote_plus(request.query)}"
    print(f"Loading {url} ...")
    checkpoint("Navigate to Google site search for Motley Fool")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Scroll to load content
    for _ in range(3):
        page.evaluate("window.scrollBy(0, 600)")
        page.wait_for_timeout(800)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    checkpoint("Extract article listings")
    items_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();

        // Extract from Google search results linking to fool.com
        const links = document.querySelectorAll('a[href*="fool.com"]');
        for (const a of links) {
            if (results.length >= maxResults) break;
            const href = a.getAttribute('href') || '';
            // Only article pages (with date-like paths)
            if (!/(\/investing\/|\/stock-market\/|\/retirement\/|\/earnings\/|\/personal-finance\/|\d{4}\/\d{2}\/)/.test(href)) continue;

            const block = a.closest('div, li') || a;
            let headline = '';
            const h3 = block.querySelector('h3');
            if (h3) headline = h3.innerText.trim();
            if (!headline) headline = a.innerText.trim();
            headline = headline.split('\n')[0].trim();
            // Clean up "The Motley Fool" suffix
            headline = headline.replace(/\s*[-|]\s*The Motley Fool\s*$/i, '').trim();
            if (!headline || headline.length < 10 || seen.has(headline)) continue;
            seen.add(headline);

            const text = block.innerText || '';
            let author = '', date = '', summary = '';
            const dateM = text.match(/(\w{3}\s+\d{1,2},?\s+\d{4}|\d{1,2}\/\d{1,2}\/\d{4})/);
            if (dateM) date = dateM[1];

            // Try to get snippet/description
            const spans = block.querySelectorAll('span, div');
            for (const s of spans) {
                const st = s.innerText.trim();
                if (st.length > 50 && st.length < 300 && !seen.has(st)) {
                    summary = st.slice(0, 200);
                    break;
                }
            }

            results.push({ headline: headline.slice(0, 120), author, date, summary });
        }
        return results;
    }""", request.max_results)

    result = ArticleResult(articles=[Article(**a) for a in items_data])

    print("\n" + "=" * 60)
    print(f"Motley Fool: {request.query}")
    print("=" * 60)
    for a in result.articles:
        print(f"  {a.headline}")
        print(f"    Author: {a.author}  Date: {a.date}")
        print(f"    Summary: {a.summary[:80]}...")
    print(f"\n  Total: {len(result.articles)} articles")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("fool_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = fool_search(page, ArticleRequest())
            print(f"\nReturned {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
