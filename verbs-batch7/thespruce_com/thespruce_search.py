"""
Auto-generated Playwright script (Python)
The Spruce – Article Search

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
    search_query: str = "best indoor plants low light"
    max_results: int = 5


@dataclass
class ArticleResult:
    title: str = ""


@dataclass
class SearchResult:
    articles: List[ArticleResult] = field(default_factory=list)


def thespruce_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search The Spruce for articles."""
    print(f"  Query: {request.search_query}\n")

    query_encoded = request.search_query.replace(" ", "+")
    url = f"https://www.thespruce.com/search?q={query_encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = SearchResult()

    checkpoint("Extract search results")
    js_code = r"""(max) => {
        const body = document.body.innerText;
        const lines = body.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find "Search Results"
        let startIdx = 0;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === 'Search Results') { startIdx = i + 1; break; }
        }
        const articles = [];
        for (let i = startIdx; i < lines.length && articles.length < max; i++) {
            const line = lines[i];
            // Stop at pagination
            if (/^\d+$/.test(line) || line === 'Next') break;
            if (line.length > 10) {
                articles.push({title: line});
            }
        }
        return articles;
    }"""
    articles_data = page.evaluate(js_code, request.max_results)

    for ad in articles_data:
        a = ArticleResult()
        a.title = ad.get("title", "")
        result.articles.append(a)

    for i, a in enumerate(result.articles, 1):
        print(f"  Article {i}: {a.title}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("thespruce")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = thespruce_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
