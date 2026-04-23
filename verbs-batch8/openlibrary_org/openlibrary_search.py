import os
import sys
import shutil
import time
from dataclasses import dataclass, field
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class OpenlibrarySearchRequest:
    search_query: str = "machine learning"
    max_results: int = 5


@dataclass
class OpenlibrarySearchItem:
    title: str = ""
    author: str = ""
    first_publish_year: str = ""
    publisher: str = ""
    num_editions: int = 0
    isbn: str = ""
    subjects: str = ""


@dataclass
class OpenlibrarySearchResult:
    items: List[OpenlibrarySearchItem] = field(default_factory=list)


def openlibrary_search(page, request: OpenlibrarySearchRequest) -> OpenlibrarySearchResult:
    url = f"https://openlibrary.org/search?q={request.search_query}"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    items = page.evaluate("""() => {
        const results = [];
        const rows = document.querySelectorAll('.searchResultItem, [class*="search-result"], li[class*="book"]');
        for (let i = 0; i < rows.length; i++) {
            const el = rows[i];
            const titleEl = el.querySelector('.booktitle a, h3 a, [class*="title"] a');
            const authorEl = el.querySelector('.bookauthor a, [class*="author"] a');
            const yearEl = el.querySelector('.publishedYear, [class*="year"], [class*="date"]');
            const publisherEl = el.querySelector('.publisher, [class*="publisher"]');
            const editionsEl = el.querySelector('.editioncount, [class*="edition"]');
            const isbnEl = el.querySelector('[class*="isbn"]');
            const subjectsEl = el.querySelector('[class*="subject"]');
            const edText = editionsEl ? editionsEl.innerText.trim() : '0';
            const edMatch = edText.match(/(\\d+)/);
            results.push({
                title: titleEl ? titleEl.innerText.trim() : '',
                author: authorEl ? authorEl.innerText.trim() : '',
                first_publish_year: yearEl ? yearEl.innerText.trim().replace(/[^0-9]/g, '') : '',
                publisher: publisherEl ? publisherEl.innerText.trim() : '',
                num_editions: edMatch ? parseInt(edMatch[1]) : 0,
                isbn: isbnEl ? isbnEl.innerText.trim() : '',
                subjects: subjectsEl ? subjectsEl.innerText.trim() : ''
            });
        }
        return results;
    }""")

    result = OpenlibrarySearchResult()
    for item in items[: request.max_results]:
        result.items.append(
            OpenlibrarySearchItem(
                title=item.get("title", ""),
                author=item.get("author", ""),
                first_publish_year=item.get("first_publish_year", ""),
                publisher=item.get("publisher", ""),
                num_editions=item.get("num_editions", 0),
                isbn=item.get("isbn", ""),
                subjects=item.get("subjects", ""),
            )
        )

    checkpoint("openlibrary_search result")
    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir()
    chrome_process = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(ws_url)
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()

    try:
        request = OpenlibrarySearchRequest(search_query="machine learning", max_results=5)
        result = openlibrary_search(page, request)
        print(f"Found {len(result.items)} books")
        for i, item in enumerate(result.items):
            print(f"  {i+1}. {item.title} by {item.author} ({item.first_publish_year})")
            print(f"     Publisher: {item.publisher} | Editions: {item.num_editions}")
            print(f"     ISBN: {item.isbn}")
            print(f"     Subjects: {item.subjects}")
    finally:
        browser.close()
        pw.stop()
        chrome_process.terminate()
        shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger

    run_with_debugger(test_func)
