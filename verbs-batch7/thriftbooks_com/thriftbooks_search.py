"""
Auto-generated Playwright script (Python)
ThriftBooks – Book Search

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
    search_query: str = "1984 George Orwell"
    max_results: int = 5


@dataclass
class BookResult:
    title: str = ""
    author: str = ""
    price: str = ""
    condition: str = ""
    format: str = ""


@dataclass
class SearchResult:
    books: List[BookResult] = field(default_factory=list)


def thriftbooks_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search ThriftBooks for books."""
    print(f"  Query: {request.search_query}\n")

    query_encoded = request.search_query.replace(" ", "+")
    url = f"https://www.thriftbooks.com/browse/?b.search={query_encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = SearchResult()

    checkpoint("Extract book results")
    js_code = r"""(max) => {
        const body = document.body.innerText;
        const lines = body.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find start of results - look for first "By " author line after filter section
        let startIdx = 0;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === 'Exclude') { startIdx = i + 1; break; }
        }
        const books = [];
        let i = startIdx;
        while (i < lines.length && books.length < max) {
            const title = lines[i];
            if (!title || title === 'Visit The Spruce' || /^(1|2|3)\s*$/.test(title)) break;
            i++;
            if (i >= lines.length) break;
            // Author line starts with "By "
            let author = '';
            if (lines[i] && lines[i].startsWith('By ')) {
                author = lines[i].replace('By ', '');
                i++;
            }
            // Price - may be "$" on one line and number on next, or "$X.XX" on one line
            let price = '';
            if (i < lines.length) {
                if (lines[i] === '$' && i + 1 < lines.length && /^[\d,.]+$/.test(lines[i+1])) {
                    price = '$' + lines[i+1];
                    i += 2;
                } else if (/^\$\s*[\d,.]+$/.test(lines[i])) {
                    price = lines[i];
                    i++;
                }
            }
            // Skip "Save $X!" line if present
            if (i < lines.length && lines[i].startsWith('Save ')) i++;
            // Format line
            let format = '';
            if (i < lines.length && lines[i].startsWith('Format:')) {
                format = lines[i].replace('Format: ', '');
                i++;
            }
            // Condition line
            let condition = '';
            if (i < lines.length && lines[i].startsWith('Condition:')) {
                condition = lines[i].replace('Condition: ', '');
                i++;
            }
            // Skip remaining lines (Add To Cart, See All, Backorder)
            while (i < lines.length && (lines[i].startsWith('Add To') || lines[i].startsWith('See ') || lines[i] === 'Backorder')) i++;
            if (title && price) {
                books.push({title, author, price, condition, format});
            }
        }
        return books;
    }"""
    books_data = page.evaluate(js_code, request.max_results)

    for bd in books_data:
        b = BookResult()
        b.title = bd.get("title", "")
        b.author = bd.get("author", "")
        b.price = bd.get("price", "")
        b.condition = bd.get("condition", "")
        b.format = bd.get("format", "")
        result.books.append(b)

    for i, b in enumerate(result.books, 1):
        print(f"\n  Book {i}:")
        print(f"    Title:     {b.title}")
        print(f"    Author:    {b.author}")
        print(f"    Price:     {b.price}")
        print(f"    Condition: {b.condition}")
        print(f"    Format:    {b.format}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("thriftbooks")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = thriftbooks_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.books)} books")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
