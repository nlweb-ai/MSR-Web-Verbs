"""
Playwright script (Python) — Bookshop.org Search
Search for books on Bookshop.org.
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
class BookshopSearchRequest:
    query: str = "science fiction"
    max_results: int = 5


@dataclass
class BookItem:
    title: str = ""
    author: str = ""
    price: str = ""
    format: str = ""


@dataclass
class BookshopSearchResult:
    query: str = ""
    items: List[BookItem] = field(default_factory=list)


def search_bookshop(page: Page, request: BookshopSearchRequest) -> BookshopSearchResult:
    """Search Bookshop.org for books."""
    encoded = quote_plus(request.query)
    url = f"https://bookshop.org/search?keywords={encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = BookshopSearchResult(query=request.query)

    checkpoint("Extract books")
    js_code = """(max) => {
        const items = [];
        const headings = document.querySelectorAll('a h2');
        for (const h of headings) {
            if (items.length >= max) break;
            const card = h.closest('a').parentElement;
            if (!card) continue;
            const lines = card.innerText.split('\\n').map(l => l.trim()).filter(l => l);

            let title = h.textContent.trim();
            if (!title || title.length < 3 || title.length > 200) continue;
            if (items.some(i => i.title === title)) continue;

            // After title, next non-empty line is author
            let author = '';
            let format = '';
            let price = '';
            const titleIdx = lines.indexOf(title);
            if (titleIdx >= 0 && titleIdx + 1 < lines.length) {
                author = lines[titleIdx + 1];
            }
            for (const line of lines) {
                if (line.match(/^(Paperback|Hardcover|Audio|eBook)/i)) format = line;
                const pm = line.match(/^(\\$[\\d,.]+)$/);
                if (pm && !price) price = pm[1];
            }

            items.push({title: title, author: author, price: price, format: format});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = BookItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.price = d.get("price", "")
        item.format = d.get("format", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} books for '{request.query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Author: {item.author}  Price: {item.price}  Format: {item.format}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("bookshop")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_bookshop(page, BookshopSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} books")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
