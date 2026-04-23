"""
Auto-generated Playwright script (Python)
CoinDesk – Search for cryptocurrency news articles by keyword
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CoindeskSearchRequest:
    search_query: str = "bitcoin"
    max_results: int = 5


@dataclass
class CoindeskArticleItem:
    title: str = ""
    author: str = ""
    publish_date: str = ""
    category: str = ""
    summary: str = ""


@dataclass
class CoindeskSearchResult:
    items: List[CoindeskArticleItem] = field(default_factory=list)


# Search for cryptocurrency news articles on CoinDesk by keyword.
def coindesk_search(page: Page, request: CoindeskSearchRequest) -> CoindeskSearchResult:
    """Search for cryptocurrency news articles on CoinDesk."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://www.coindesk.com/search?s={query}&sort=date"
    print(f"Loading {url}...")
    checkpoint("Navigate to CoinDesk search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = CoindeskSearchResult()

    checkpoint("Extract article listings")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();
        
        // Strategy 1: find article links
        const links = document.querySelectorAll('a[href]');
        for (const a of links) {
            if (items.length >= max) break;
            const href = a.getAttribute('href') || '';
            // CoinDesk article links have date-based paths
            if (!href.match(/\\/\\d{4}\\/\\d{2}\\/\\d{2}\\//)) continue;
            
            const text = a.innerText.trim();
            const title = text.split('\\n')[0].trim();
            if (title.length < 10 || seen.has(title)) continue;
            seen.add(title);
            
            const card = a.closest('div, li, article') || a;
            const fullText = card.innerText.trim();
            const lines = fullText.split('\\n').filter(l => l.trim());
            
            let author = '';
            let pubDate = '';
            let category = '';
            let summary = '';
            for (const line of lines) {
                if (line.match(/^by\\s+/i)) author = line.replace(/^by\\s+/i, '');
                if (line.match(/\\w+\\s+\\d{1,2},\\s+\\d{4}/)) pubDate = line;
                if (line.length > 30 && line !== title && !summary) summary = line.substring(0, 200);
            }
            
            items.push({title, author, publish_date: pubDate, category, summary});
        }
        
        // Strategy 2: headings
        if (items.length === 0) {
            const headings = document.querySelectorAll('h2, h3');
            for (const h of headings) {
                if (items.length >= max) break;
                const title = h.innerText.trim();
                if (title.length > 10 && !seen.has(title)) {
                    seen.add(title);
                    items.push({title, author: '', publish_date: '', category: '', summary: ''});
                }
            }
        }
        
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = CoindeskArticleItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.publish_date = d.get("publish_date", "")
        item.category = d.get("category", "")
        item.summary = d.get("summary", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Article {i}:")
        print(f"    Title:    {item.title}")
        print(f"    Author:   {item.author}")
        print(f"    Date:     {item.publish_date}")
        print(f"    Category: {item.category}")
        print(f"    Summary:  {item.summary[:100]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("coindesk")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = CoindeskSearchRequest()
            result = coindesk_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
