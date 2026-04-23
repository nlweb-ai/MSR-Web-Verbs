"""
Auto-generated Playwright script (Python)
Runner's World – Article Search

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
class SearchRequest:
    search_query: str = "marathon training plan"
    max_articles: int = 5


@dataclass
class Article:
    title: str = ""
    author: str = ""
    date: str = ""
    summary: str = ""


@dataclass
class SearchResult:
    articles: List[Article] = field(default_factory=list)


def runnersworld_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search Runner's World for articles."""
    print(f"  Query: {request.search_query}\n")

    # ── Navigate to search page ───────────────────────────────────────
    query_encoded = request.search_query.replace(" ", "+")
    url = f"https://www.runnersworld.com/search/?q={query_encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = SearchResult()

    # ── Extract articles via text parsing ─────────────────────────────
    checkpoint("Extract search results")
    js_code = r"""(max) => {
        const body = document.body.innerText;
        // Find the results section after "results for keyword"
        const startMatch = body.match(/\d+ results for keyword .+\n/);
        if (!startMatch) return [];
        const startIdx = body.indexOf(startMatch[0]) + startMatch[0].length;
        // Find end at "Advertisement" or footer
        let endIdx = body.indexOf('Advertisement', startIdx);
        if (endIdx < 0) endIdx = body.length;
        const section = body.substring(startIdx, endIdx);

        // Split into individual lines
        const lines = section.split('\n').map(l => l.trim()).filter(l => l.length > 0);

        const articles = [];
        let i = 0;
        // Skip "Sort By:" and "Relevance" lines
        while (i < lines.length && (lines[i].startsWith('Sort By') || lines[i] === 'Relevance')) i++;

        while (i < lines.length && articles.length < max) {
            // Title line
            const title = lines[i]; i++;
            if (!title) continue;

            // Summary line (not ALL CAPS author)
            let summary = '', author = '', date = '';
            if (i < lines.length && !lines[i].match(/^[A-Z][A-Z .,]+$/)) {
                summary = lines[i]; i++;
            }
            // Author line (ALL CAPS)
            if (i < lines.length && lines[i].match(/^[A-Z][A-Z .,]+$/)) {
                author = lines[i]; i++;
            }
            // Date line (MMM DD, YYYY)
            if (i < lines.length && lines[i].match(/^[A-Z]{3}\s+\d{1,2},\s+\d{4}$/)) {
                date = lines[i]; i++;
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
    profile_dir = get_temp_profile_dir("runnersworld")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = runnersworld_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
