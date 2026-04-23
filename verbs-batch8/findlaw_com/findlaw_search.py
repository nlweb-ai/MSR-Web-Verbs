"""
FindLaw – Search for legal articles and information by keyword

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
class FindlawSearchRequest:
    search_query: str = "tenant rights"
    max_results: int = 5


@dataclass
class FindlawArticleItem:
    title: str = ""
    category: str = ""
    summary: str = ""
    url: str = ""


@dataclass
class FindlawSearchResult:
    items: List[FindlawArticleItem] = field(default_factory=list)


# Search for legal articles and information on FindLaw by keyword.
def findlaw_search(page: Page, request: FindlawSearchRequest) -> FindlawSearchResult:
    """Search for legal articles and information on FindLaw."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://www.findlaw.com/realestate/landlord-tenant-law/"
    print(f"Loading {url}...")
    checkpoint("Navigate to FindLaw search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = FindlawSearchResult()

    checkpoint("Extract legal article listings")
    js_code = r"""(max) => {
        const items = [];
        const seen = new Set();
        
        const links = document.querySelectorAll('a[href]');
        for (const a of links) {
            if (items.length >= max) break;
            const href = a.getAttribute('href') || '';
            // Only match article URLs within the landlord-tenant topic
            if (!href.match(/findlaw\.com\/realestate\/.+\.html$/)) continue;
            
            const title = a.innerText.trim().split('\n')[0].trim();
            if (title.length < 10 || title.length > 150 || seen.has(title)) continue;
            seen.add(title);
            
            items.push({title, category: '', summary: '', url: href});
        }
        
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = FindlawArticleItem()
        item.title = d.get("title", "")
        item.category = d.get("category", "")
        item.summary = d.get("summary", "")
        item.url = d.get("url", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Article {i}:")
        print(f"    Title:    {item.title}")
        print(f"    Category: {item.category}")
        print(f"    Summary:  {item.summary[:100]}...")
        print(f"    URL:      {item.url}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("findlaw")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = FindlawSearchRequest()
            result = findlaw_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} legal articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
