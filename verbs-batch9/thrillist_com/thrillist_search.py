"""
Playwright script (Python) — Thrillist Article Search

Searches Thrillist for food, drink, and travel articles matching a query,
and extracts article titles, categories, and summaries.

Uses the user's Chrome profile for persistent login state.
"""

import os
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ThrillistSearchRequest:
    search_query: str
    max_results: int


@dataclass(frozen=True)
class ThrillistArticleItem:
    title: str
    category: str
    summary: str


@dataclass
class ThrillistSearchResult:
    articles: List[ThrillistArticleItem] = field(default_factory=list)
    error: str = ""


# Searches Thrillist for articles matching a query string,
# extracts up to max_results articles with title, category, and summary
# by parsing the search results page text content.
def thrillist_search(page: Page, request: ThrillistSearchRequest) -> ThrillistSearchResult:
    result = ThrillistSearchResult()
    try:
        from urllib.parse import quote_plus
        url = f"https://www.thrillist.com/search?q={quote_plus(request.search_query)}"
        checkpoint(f"Navigate to {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(5000)

        checkpoint("Page loaded — extracting articles")

        articles_data = page.evaluate("""(max) => {
            const results = [];
            const body = document.body.innerText;
            const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            const cats = ['EAT', 'DRINK', 'TRAVEL', 'EVENTS', 'ENTERTAINMENT', 'NEWS', 'HOME', 'HEALTH'];
            for (let i = 0; i < lines.length && results.length < max; i++) {
                if (cats.includes(lines[i]) && i + 2 < lines.length) {
                    const title = lines[i + 1];
                    const summary = lines[i + 2];
                    // Skip nav items, section headers, sponsored tags
                    if (title.startsWith('SEE ALL') || title.startsWith('Latest')) continue;
                    if (title.startsWith('PRESENTED')) continue;
                    if (title.startsWith('LOAD MORE')) continue;
                    results.push({ title, category: lines[i], summary });
                }
            }
            return results;
        }""", request.max_results)

        for item in articles_data:
            result.articles.append(ThrillistArticleItem(**item))

        checkpoint(f"Extracted {len(result.articles)} articles")

    except Exception as e:
        result.error = str(e)
    return result


def test_thrillist_search() -> None:
    request = ThrillistSearchRequest(
        search_query="best pizza Brooklyn",
        max_results=5,
    )

    print("=" * 60)
    print("  Thrillist – Article Search")
    print(f"  Query: {request.search_query}")
    print(f"  Max results: {request.max_results}")
    print("=" * 60)

    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default",
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=False,
            viewport=None,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
                "--start-maximized",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = thrillist_search(page, request)
            print(f"\nFound {len(result.articles)} articles:")
            for i, a in enumerate(result.articles, 1):
                print(f"  {i}. [{a.category}] {a.title}")
                print(f"     {a.summary[:80]}")
            if result.error:
                print(f"Error: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_thrillist_search)
