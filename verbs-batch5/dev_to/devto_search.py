"""
Auto-generated Playwright script (Python)
dev.to – Article Search
Query: React hooks

Generated on: 2026-04-18T00:43:58.466Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil, urllib.parse
from dataclasses import dataclass
from playwright.sync_api import Playwright, sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class DevToSearchRequest:
    search_query: str = "React hooks"
    max_results: int = 5


@dataclass(frozen=True)
class DevToArticle:
    title: str = ""
    author: str = ""
    publication_date: str = ""
    reactions: str = ""
    comments: str = ""


@dataclass(frozen=True)
class DevToSearchResult:
    articles: list = None  # list[DevToArticle]


def devto_search(page: Page, request: DevToSearchRequest) -> DevToSearchResult:
    """Search dev.to for articles."""
    query = request.search_query
    max_results = request.max_results
    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    # ── Navigate to search results ────────────────────────────────────
    url = f"https://dev.to/search?q={urllib.parse.quote_plus(query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to dev.to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    # ── Extract articles ──────────────────────────────────────────────
    checkpoint("Extract articles")
    results_data = page.evaluate(r"""(maxResults) => {
        const articles = document.querySelectorAll('.crayons-story');
        const results = [];
        for (const article of articles) {
            if (results.length >= maxResults) break;

            // Title from the hidden navigation link
            const titleEl = article.querySelector('.crayons-story__hidden-navigation-link');
            const title = titleEl ? titleEl.textContent.trim() : '';

            // Author from profile link
            const authorEl = article.querySelector('.crayons-story__meta a.crayons-avatar');
            const authorNameEl = article.querySelector('.crayons-story__secondary');
            let author = '';
            if (authorNameEl) {
                // Author name is in the button or first text
                const btn = authorNameEl.querySelector('button, a');
                author = btn ? btn.textContent.trim() : authorNameEl.textContent.trim().split('\n')[0].trim();
            }

            // Date from time element
            const timeEl = article.querySelector('time');
            const pubDate = timeEl ? timeEl.textContent.trim() : '';

            // Reactions and comments from detail links
            const text = article.innerText;
            const reactionsMatch = text.match(/(\d+)\s*reaction/i);
            const reactions = reactionsMatch ? reactionsMatch[1] : '0';

            const commentsMatch = text.match(/(\d+)\s*comment/i);
            const addCommentMatch = text.match(/Add Comment/i);
            const comments = commentsMatch ? commentsMatch[1] : (addCommentMatch ? '0' : '0');

            if (title) {
                results.push({ title, author, pubDate, reactions, comments });
            }
        }
        return results;
    }""", max_results)

    articles = []
    for r in results_data:
        articles.append(DevToArticle(
            title=r.get("title", ""),
            author=r.get("author", ""),
            publication_date=r.get("pubDate", ""),
            reactions=r.get("reactions", "0"),
            comments=r.get("comments", "0"),
        ))

    # ── Print results ─────────────────────────────────────────────────
    print("=" * 60)
    print(f'dev.to - "{query}" Articles')
    print("=" * 60)
    for idx, a in enumerate(articles, 1):
        print(f"\n{idx}. {a.title}")
        print(f"   Author: {a.author} | Date: {a.publication_date}")
        print(f"   Reactions: {a.reactions} | Comments: {a.comments}")

    print(f"\nFound {len(articles)} articles")
    return DevToSearchResult(articles=articles)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("dev_to")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = devto_search(page, DevToSearchRequest())
            print(f"\nReturned {len(result.articles or [])} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
