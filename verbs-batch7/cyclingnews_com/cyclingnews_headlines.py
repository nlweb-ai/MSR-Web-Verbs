"""
Auto-generated Playwright script (Python)
CyclingNews – Latest Headlines

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class HeadlinesRequest:
    max_articles: int = 5


@dataclass
class Article:
    title: str = ""
    author: str = ""
    date: str = ""
    summary: str = ""


@dataclass
class HeadlinesResult:
    articles: List[Article] = field(default_factory=list)


def cyclingnews_headlines(page: Page, request: HeadlinesRequest) -> HeadlinesResult:
    """Extract latest cycling news headlines from CyclingNews."""
    print(f"  Max articles: {request.max_articles}\n")

    # ── Navigate to news page ─────────────────────────────────────────
    url = "https://www.cyclingnews.com/news/"
    print(f"Loading {url}...")
    checkpoint("Navigate to CyclingNews")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = HeadlinesResult()

    # ── Extract articles from listing cards ───────────────────────────
    checkpoint("Extract article cards")
    js_code = r"""(max) => {
        const cards = document.querySelectorAll('.listingResult');
        const articles = [];
        for (let i = 0; i < cards.length && articles.length < max; i++) {
            const card = cards[i];
            const link = card.querySelector('a.article-link');
            const title = link ? (link.getAttribute('aria-label') || '').trim() : '';
            if (!title) continue;

            const text = card.innerText.trim();
            const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);

            // Parse "By Author published X hours/days ago"
            let author = '', date = '';
            const byLine = lines.find(l => l.startsWith('By '));
            if (byLine) {
                const pubMatch = byLine.match(/^By\s+(.+?)\s+published\s+(.+)$/);
                if (pubMatch) {
                    author = pubMatch[1];
                    date = pubMatch[2];
                }
            }

            // Summary is the line after the byline that's not just a category tag
            let summary = '';
            const byIdx = lines.indexOf(byLine);
            if (byIdx >= 0 && byIdx + 1 < lines.length) {
                const next = lines[byIdx + 1];
                // Strip leading category label
                summary = next.replace(/^(?:NEWS|FEATURE|HOW TO WATCH|RACE RESULTS|TECH)\s*/i, '').trim();
            }

            articles.push({title, author, date, summary});
        }
        return articles;
    }"""
    articles_data = page.evaluate(js_code, request.max_articles)

    for ad in articles_data:
        article = Article()
        article.title = ad.get("title", "")
        article.author = ad.get("author", "")
        article.date = ad.get("date", "")
        article.summary = ad.get("summary", "")
        result.articles.append(article)

    # ── Print results ─────────────────────────────────────────────────
    for i, a in enumerate(result.articles, 1):
        print(f"\n  Article {i}:")
        print(f"    Title:   {a.title}")
        print(f"    Author:  {a.author}")
        print(f"    Date:    {a.date}")
        print(f"    Summary: {a.summary}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("cyclingnews")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = HeadlinesRequest()
            result = cyclingnews_headlines(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
