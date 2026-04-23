"""
Playwright script (Python) — Goodreads Quotes Browser
Browse quotes by tag on Goodreads.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GoodreadsQuotesRequest:
    tag: str = "inspirational"
    max_results: int = 5


@dataclass
class QuoteItem:
    text: str = ""
    author: str = ""
    book: str = ""
    likes: str = ""


@dataclass
class GoodreadsQuotesResult:
    tag: str = ""
    items: List[QuoteItem] = field(default_factory=list)


# Browses Goodreads quotes by tag and returns up to max_results quotes
# with text, author, book title, and number of likes.
def browse_goodreads_quotes(page: Page, request: GoodreadsQuotesRequest) -> GoodreadsQuotesResult:
    import urllib.parse
    url = f"https://www.goodreads.com/quotes/tag/{urllib.parse.quote_plus(request.tag)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to quotes page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = GoodreadsQuotesResult(tag=request.tag)

    checkpoint("Extract quotes")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        const quotes = document.querySelectorAll('.quote.mediumText');
        for (const q of quotes) {
            if (results.length >= max) break;
            const lines = q.innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 3) continue;
            // Find author line (starts with ―)
            let authorIdx = -1;
            for (let i = 0; i < lines.length; i++) {
                if (lines[i].trim().startsWith('\\u2015')) { authorIdx = i; break; }
            }
            if (authorIdx < 1) continue;
            // Quote text = all lines before author
            let text = lines.slice(0, authorIdx).join(' ').trim();
            text = text.replace(/^[\\u201C"]/,'').replace(/[\\u201D"]$/,'').trim();
            if (!text || seen.has(text)) continue;
            seen.add(text);
            // Author: remove leading ―
            let authorLine = lines[authorIdx].trim().replace(/^\\u2015\\s*/, '');
            // May have ", Book Title" appended
            let author = authorLine, book = '';
            const commaIdx = authorLine.indexOf(',');
            if (commaIdx > 0) {
                author = authorLine.substring(0, commaIdx).trim();
                book = authorLine.substring(commaIdx + 1).trim();
            }
            // Likes: find "NNNN likes" line
            let likes = '';
            for (let i = authorIdx + 1; i < lines.length; i++) {
                const m = lines[i].match(/(\\d[\\d,]*)\\s+likes?/);
                if (m) { likes = m[1]; break; }
            }
            results.push({text: text.substring(0, 300), author, book, likes});
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = QuoteItem()
        item.text = d.get("text", "")
        item.author = d.get("author", "")
        item.book = d.get("book", "")
        item.likes = d.get("likes", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} quotes for tag '{request.tag}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. \"{item.text[:100]}...\"")
        print(f"     Author: {item.author}  Book: {item.book}  Likes: {item.likes}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("goodreads")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = browse_goodreads_quotes(page, GoodreadsQuotesRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} quotes")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
