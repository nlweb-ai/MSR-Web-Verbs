"""
Hunker – Search for home improvement articles

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
class HunkerSearchRequest:
    search_query: str = "kitchen remodel"
    max_results: int = 5


@dataclass
class HunkerArticleItem:
    title: str = ""
    author: str = ""
    category: str = ""
    summary: str = ""
    image_url: str = ""


@dataclass
class HunkerSearchResult:
    items: List[HunkerArticleItem] = field(default_factory=list)


# Search for home improvement articles on Hunker.
def hunker_search(page: Page, request: HunkerSearchRequest) -> HunkerSearchResult:
    """Search for home improvement articles on Hunker."""
    print(f"  Query: {request.search_query}")
    print(f"  Max results: {request.max_results}\n")

    query_encoded = request.search_query.replace(" ", "+")
    url = f"https://www.hunker.com/search?q={query_encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Hunker search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = HunkerSearchResult()

    checkpoint("Extract article listings")
    js_code = """(max) => {
        const cards = document.querySelectorAll('[class*="card"], [class*="result"], [class*="article"], [class*="search-result"], [class*="listing"], article');
        const items = [];
        for (const card of cards) {
            if (items.length >= max) break;
            const titleEl = card.querySelector('h2, h3, h4, [class*="title"], [class*="Title"], a[class*="title"]');
            const authorEl = card.querySelector('[class*="author"], [class*="Author"], [class*="byline"], [class*="writer"]');
            const categoryEl = card.querySelector('[class*="category"], [class*="Category"], [class*="tag"], [class*="topic"]');
            const summaryEl = card.querySelector('p, [class*="summary"], [class*="description"], [class*="snippet"], [class*="excerpt"]');
            const imgEl = card.querySelector('img[src], img[data-src]');

            const title = titleEl ? titleEl.textContent.trim() : '';
            const author = authorEl ? authorEl.textContent.trim() : '';
            const category = categoryEl ? categoryEl.textContent.trim() : '';
            const summary = summaryEl ? summaryEl.textContent.trim() : '';
            const image_url = imgEl ? (imgEl.src || imgEl.dataset.src || '') : '';

            if (title) {
                items.push({title, author, category, summary, image_url});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = HunkerArticleItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.category = d.get("category", "")
        item.summary = d.get("summary", "")
        item.image_url = d.get("image_url", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Article {i}:")
        print(f"    Title:    {item.title}")
        print(f"    Author:   {item.author}")
        print(f"    Category: {item.category}")
        print(f"    Summary:  {item.summary[:80]}")
        print(f"    Image:    {item.image_url[:80]}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("hunker")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = HunkerSearchRequest()
            result = hunker_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
