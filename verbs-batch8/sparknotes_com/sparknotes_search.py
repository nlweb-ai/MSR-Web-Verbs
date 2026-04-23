"""
SparkNotes – Search for study guides by keyword

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class SparknotesSearchRequest:
    search_query: str = "hamlet"
    max_results: int = 5


@dataclass
class SparknotesGuideItem:
    title: str = ""
    author: str = ""
    type: str = ""
    summary: str = ""
    url: str = ""


@dataclass
class SparknotesSearchResult:
    items: List[SparknotesGuideItem] = field(default_factory=list)


# Search for study guides on SparkNotes by keyword.
def sparknotes_search(page: Page, request: SparknotesSearchRequest) -> SparknotesSearchResult:
    """Search for study guides on SparkNotes."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://www.sparknotes.com/lit/"
    print(f"Loading {url}...")
    checkpoint("Navigate to SparkNotes search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = SparknotesSearchResult()

    checkpoint("Extract study guide listings")
    js_code = """(max) => {
        const links = document.querySelectorAll('a[href]');
        const items = [];
        const seen = new Set();
        for (const a of links) {
            if (items.length >= max) break;
            const href = a.getAttribute('href') || '';
            // Match sparknotes content links like /lit/, /shakespeare/, /poetry/, /philosophy/, /biography/
            if (!href.match(/sparknotes\\.com\\/(lit|shakespeare|poetry|philosophy|biography|film|short-stories|math|science|history|us-history)\\/[^/]+/)) continue;
            const text = a.textContent.trim();
            if (!text || text.length < 3 || text.length > 200) continue;
            if (seen.has(href)) continue;
            seen.add(href);
            items.push({title: text, author: '', type: '', summary: '', url: href});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = SparknotesGuideItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.type = d.get("type", "")
        item.summary = d.get("summary", "")
        item.url = d.get("url", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Guide {i}:")
        print(f"    Title:   {item.title}")
        print(f"    Author:  {item.author}")
        print(f"    Type:    {item.type}")
        print(f"    Summary: {item.summary[:100]}...")
        print(f"    URL:     {item.url}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("sparknotes")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SparknotesSearchRequest()
            result = sparknotes_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} study guides")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
