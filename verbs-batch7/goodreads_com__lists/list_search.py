"""
Auto-generated Playwright script (Python)
Goodreads – Search lists and extract top books

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re, urllib.parse
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ListSearchRequest:
    search_query: str = "best science fiction"
    max_results: int = 5


@dataclass
class Book:
    rank: str = ""
    title: str = ""
    author: str = ""
    score: str = ""


@dataclass
class ListSearchResult:
    list_title: str = ""
    books: List[Book] = field(default_factory=list)


def list_search(page: Page, request: ListSearchRequest) -> ListSearchResult:
    """Search Goodreads lists and extract top books from the first matching list."""
    print(f"  Query: {request.search_query}")
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Navigate to Goodreads list search")
    q = urllib.parse.quote_plus(request.search_query)
    page.goto(f"https://www.goodreads.com/search?q={q}&search_type=lists", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Click first matching list")
    first_list_url = page.evaluate(r"""() => {
        const link = document.querySelector('.listTitle');
        return link ? link.href : '';
    }""")

    if not first_list_url:
        print("  No lists found.")
        return ListSearchResult()

    page.goto(first_list_url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract list title and books")
    result = ListSearchResult()

    data = page.evaluate(
        r"""(max) => {
            // List title from breadcrumb or page title
            const h1 = document.querySelector('h1.gr-h1, .leftContainer h1');
            let listTitle = h1 ? h1.textContent.trim() : '';
            if (!listTitle || listTitle === 'Score') {
                // Fallback to page title (strip " (NNN books)" suffix)
                listTitle = document.title.replace(/\s*\(\d+\s*books?\)\s*$/, '').trim();
            }

            // Books from table rows
            const rows = document.querySelectorAll('tr[itemtype="http://schema.org/Book"]');
            const books = [];
            for (let i = 0; i < rows.length && books.length < max; i++) {
                const row = rows[i];

                const rankEl = row.querySelector('td.number');
                const rank = rankEl ? rankEl.textContent.trim() : String(i + 1);

                const titleEl = row.querySelector('.bookTitle span[itemprop="name"]');
                const title = titleEl ? titleEl.textContent.trim() : '';

                const authorEl = row.querySelector('.authorName span[itemprop="name"]');
                const author = authorEl ? authorEl.textContent.trim() : '';

                // Score is in text like "score: 1,003,344"
                const rowText = row.textContent;
                const scoreMatch = rowText.match(/score:\s*([\d,]+)/);
                const score = scoreMatch ? scoreMatch[1].replace(/,$/, '') : '';

                if (title) {
                    books.push({rank, title, author, score});
                }
            }
            return {listTitle, books};
        }""",
        request.max_results,
    )

    result.list_title = data.get("listTitle", "")
    for item in data.get("books", []):
        b = Book()
        b.rank = item.get("rank", "")
        b.title = item.get("title", "")
        b.author = item.get("author", "")
        b.score = item.get("score", "")
        result.books.append(b)

    print(f"  List: {result.list_title}\n")
    for i, b in enumerate(result.books):
        print(f"  Book {i + 1}:")
        print(f"    Rank:   {b.rank}")
        print(f"    Title:  {b.title}")
        print(f"    Author: {b.author}")
        print(f"    Score:  {b.score}")
        print()

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
            request = ListSearchRequest()
            result = list_search(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.books)} books in list: {result.list_title}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
