"""
Axios – Search for news articles by keyword

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class AxiosSearchRequest:
    search_query: str = "artificial intelligence"
    max_results: int = 5


@dataclass
class AxiosArticleItem:
    title: str = ""
    author: str = ""
    publish_date: str = ""
    category: str = ""
    summary: str = ""


@dataclass
class AxiosSearchResult:
    items: List[AxiosArticleItem] = field(default_factory=list)


# Search for news articles on Axios by keyword.
def axios_search(page: Page, request: AxiosSearchRequest) -> AxiosSearchResult:
    """Search for news articles on Axios."""
    print(f"  Query: {request.search_query}\n")

    query = quote_plus(request.search_query)
    url = f"https://www.axios.com/technology"
    print(f"Loading {url}...")
    checkpoint("Navigate to Axios technology section")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = AxiosSearchResult()

    checkpoint("Extract article listings")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();
        
        // Try to find article links
        const links = document.querySelectorAll('a[href]');
        for (const a of links) {
            if (items.length >= max) break;
            const href = a.getAttribute('href') || '';
            // Axios article URLs contain date patterns like /2024/01/01/
            if (!href.match(/\\/\\d{4}\\/\\d{2}\\/\\d{2}\\//)) continue;
            
            const text = a.innerText.trim();
            const title = text.split('\\n')[0].trim();
            if (title.length < 10 || seen.has(title)) continue;
            seen.add(title);
            
            const card = a.closest('li, div, article') || a;
            const fullText = card.innerText.trim();
            const lines = fullText.split('\\n').filter(l => l.trim());
            
            let author = '';
            let pubDate = '';
            let category = '';
            let summary = '';
            
            for (const line of lines) {
                if (line.match(/^by\\s+/i)) author = line.replace(/^by\\s+/i, '');
                if (line.match(/\\w+\\s+\\d{1,2},\\s+\\d{4}/)) pubDate = line;
                if (line.length > 30 && line !== title) summary = line.substring(0, 200);
            }
            
            items.push({title, author, publish_date: pubDate, category, summary});
        }
        
        // Fallback: look for h2/h3 headings
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
        item = AxiosArticleItem()
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
    profile_dir = get_temp_profile_dir("axios")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = AxiosSearchRequest()
            result = axios_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
