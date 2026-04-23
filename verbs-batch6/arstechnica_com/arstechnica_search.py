"""
Auto-generated Playwright script (Python)
Ars Technica – Article Search
Query: "artificial intelligence regulation"

Generated on: 2026-04-18T04:48:12.432Z
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
    query: str = "artificial intelligence regulation"
    max_articles: int = 5


@dataclass
class Article:
    headline: str = ""
    author: str = ""
    date: str = ""
    summary: str = ""


@dataclass
class ArticleResult:
    articles: list = field(default_factory=list)


def arstechnica_search(page: Page, request: ArticleRequest) -> ArticleResult:
    """Search Ars Technica for articles and extract details."""
    print(f"  Query: {request.query}\n")

    # ── Step 1: Search Ars Technica ───────────────────────────────────
    url = f"https://arstechnica.com/search/?q={quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Ars Technica search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Step 2: Collect article URLs from search results ──────────────
    checkpoint("Collect article URLs from search results")
    article_urls = page.evaluate(r"""(maxArticles) => {
        const urls = [];
        const seen = new Set();
        const links = document.querySelectorAll('.gsc-thumbnail-inside a.gs-title');
        for (const a of links) {
            if (urls.length >= maxArticles) break;
            const href = a.getAttribute('data-ctorig') || a.href || '';
            if (!href || seen.has(href) || !href.includes('arstechnica.com')) continue;
            seen.add(href);
            urls.push(href);
        }
        return urls;
    }""", request.max_articles)

    # ── Step 3: Visit each article to extract details ─────────────────
    articles_data = []
    for i, article_url in enumerate(article_urls):
        checkpoint(f"Extract article {i + 1} details")
        page.goto(article_url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        data = page.evaluate(r"""() => {
            const h1 = document.querySelector('h1');
            const headline = h1 ? h1.innerText.trim() : '';

            const authorEl = document.querySelector('[itemprop="author"], a[href*="/author/"], [rel="author"]');
            const author = authorEl ? authorEl.innerText.trim() : '';

            const timeEl = document.querySelector('time');
            let date = '';
            if (timeEl) {
                date = timeEl.innerText.trim() || timeEl.getAttribute('datetime') || '';
            }

            // Summary: first substantial paragraph or the sub-heading
            const paras = document.querySelectorAll('article p, .article-content p, p');
            let summary = '';
            for (const p of paras) {
                const t = p.innerText.trim();
                if (t.length > 40 && !t.includes('cookie') && !t.includes('privacy')
                    && !t.includes('Consent Management') && !t.includes('Tracking Technologies')
                    && !t.includes('AdChoices') && !t.includes('opt out')) {
                    summary = t.slice(0, 300);
                    break;
                }
            }

            return { headline, author, date, summary };
        }""")
        articles_data.append(data)

    result = ArticleResult(
        articles=[Article(headline=a['headline'], author=a['author'], date=a['date'], summary=a['summary']) for a in articles_data]
    )

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Ars Technica: {request.query}")
    print("=" * 60)
    for i, a in enumerate(articles_data, 1):
        print(f"\n  {i}. {a['headline']}")
        print(f"     Author: {a['author']}")
        print(f"     Date: {a['date']}")
        print(f"     Summary: {a['summary']}")
    print(f"\n  Total: {len(result.articles)} articles")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("arstechnica_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = arstechnica_search(page, ArticleRequest())
            print(f"\nReturned {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
