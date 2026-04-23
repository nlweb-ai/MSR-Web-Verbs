"""
Auto-generated Playwright script (Python)
Literary Hub – Recent book reviews / articles

Uses CDP-launched Chrome to avoid bot detection.
Collects article URLs from homepage → visits each → extracts details.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ReviewSearchRequest:
    max_results: int = 5


@dataclass
class Article:
    title: str = ""
    author: str = ""
    date: str = ""
    summary: str = ""


@dataclass
class ReviewSearchResult:
    articles: List[Article] = field(default_factory=list)


def review_search(page: Page, request: ReviewSearchRequest) -> ReviewSearchResult:
    """Search Literary Hub for recent articles/reviews."""
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Navigate to Literary Hub")
    page.goto("https://lithub.com/", wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    checkpoint("Collect article URLs from THE LATEST section")
    articles_data = page.evaluate(
        r"""(max) => {
            const h2s = document.querySelectorAll('h2 a[href]');
            const seen = new Set();
            const results = [];
            for (const a of h2s) {
                if (results.length >= max) break;
                const href = a.href;
                if (seen.has(href) || !href.includes('lithub.com/')) continue;
                // Skip category/tag pages
                if (href.includes('/category/') || href.includes('/tag/')) continue;
                seen.add(href);
                // Try to get author from nearby "BY XXX" text
                const parent = a.closest('.content-container') || a.closest('div');
                let author = '';
                if (parent) {
                    const text = parent.innerText;
                    const byMatch = text.match(/^BY\s+(.+)/m);
                    if (byMatch) author = byMatch[1].trim();
                }
                results.push({url: href, author: author});
            }
            return results;
        }""",
        request.max_results + 5,  # collect extras in case some fail
    )

    result = ReviewSearchResult()

    for i, item in enumerate(articles_data):
        if len(result.articles) >= request.max_results:
            break
        url = item.get("url", "")
        listing_author = item.get("author", "")
        
        checkpoint(f"Visit article {i + 1}")
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        info = page.evaluate(r"""() => {
            // Title from h1
            const h1 = document.querySelector('h1');
            const title = h1 ? h1.textContent.trim() : '';

            // Date - from .post-date or meta
            let date = '';
            const dateEl = document.querySelector('.post-date');
            if (dateEl) {
                // post-date may contain "LITERARY HUB\nApril 17, 2026" - extract just date
                const dateMatch = dateEl.textContent.match(/((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})/i);
                if (dateMatch) date = dateMatch[1];
            }
            if (!date) {
                const meta = document.querySelector('meta[property="article:published_time"]');
                if (meta) date = meta.getAttribute('content') || '';
            }

            // Author - from byline or meta
            let author = '';
            const authorEl = document.querySelector('[rel="author"], .author-name, [class*="byline"] a');
            if (authorEl) {
                author = authorEl.textContent.trim();
            }
            if (!author) {
                const body = document.body.innerText;
                const byMatch = body.match(/^BY\s+([A-Z][A-Z\s.]+)$/m);
                if (byMatch) author = byMatch[1].trim();
            }

            // Summary from meta description
            let summary = '';
            const metaDesc = document.querySelector('meta[property="og:description"]');
            if (metaDesc) summary = metaDesc.getAttribute('content') || '';
            if (!summary) {
                const firstP = document.querySelector('.entry-content p, article p');
                if (firstP) summary = firstP.textContent.trim().slice(0, 200);
            }

            return {title, author, date, summary: summary.slice(0, 200)};
        }""")

        a = Article()
        a.title = info.get("title", "")
        a.author = info.get("author", "") or listing_author
        a.date = info.get("date", "")
        a.summary = info.get("summary", "")
        result.articles.append(a)

    for i, a in enumerate(result.articles):
        print(f"  Article {i + 1}:")
        print(f"    Title:   {a.title}")
        print(f"    Author:  {a.author}")
        print(f"    Date:    {a.date}")
        print(f"    Summary: {a.summary[:100]}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("lithub")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = ReviewSearchRequest()
            result = review_search(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
