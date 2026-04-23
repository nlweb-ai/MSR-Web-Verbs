"""
Playwright script (Python) — HowStuffWorks Article Search
Search HowStuffWorks for educational articles.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class HowStuffWorksRequest:
    search_query: str = "how solar panels work"
    max_results: int = 5


@dataclass
class ArticleItem:
    title: str = ""
    summary: str = ""


@dataclass
class HowStuffWorksResult:
    query: str = ""
    items: List[ArticleItem] = field(default_factory=list)


# Searches HowStuffWorks for articles matching the query and returns
# up to max_results articles with title and summary.
def search_howstuffworks(page: Page, request: HowStuffWorksRequest) -> HowStuffWorksResult:
    import urllib.parse
    url = f"https://www.howstuffworks.com/search.php?terms={urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = HowStuffWorksResult(query=request.search_query)

    checkpoint("Extract article listings")
    js_code = """(max) => {
        const results = [];
        // HowStuffWorks search uses H4 for article titles
        const h4s = document.querySelectorAll('h4');
        for (const h4 of h4s) {
            if (results.length >= max) break;
            const title = h4.innerText.trim();
            if (!title || title.length < 5) continue;
            if (results.some(r => r.title === title)) continue;

            const card = h4.closest('div, li') || h4.parentElement;

            let summary = '';
            if (card) {
                const lines = card.innerText.split('\\n').filter(l => l.trim());
                // lines: title, url, summary
                if (lines.length >= 3) summary = lines[2].trim().substring(0, 200);
            }

            results.push({ title, summary });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ArticleItem()
        item.title = d.get("title", "")
        item.summary = d.get("summary", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} articles for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        if item.summary:
            print(f"     {item.summary[:100]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("howstuffworks")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_howstuffworks(page, HowStuffWorksRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
