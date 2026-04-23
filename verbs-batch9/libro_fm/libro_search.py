"""
Playwright script (Python) — Libro.fm Audiobook Search
Search Libro.fm for audiobooks and extract details.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class LibroRequest:
    search_query: str = "self-improvement"
    max_results: int = 5


@dataclass
class AudiobookItem:
    title: str = ""
    author: str = ""


@dataclass
class LibroResult:
    query: str = ""
    items: List[AudiobookItem] = field(default_factory=list)


# Searches Libro.fm for audiobooks matching the query and returns
# up to max_results audiobooks with title and author.
def search_libro_audiobooks(page: Page, request: LibroRequest) -> LibroResult:
    import urllib.parse
    url = f"https://libro.fm/search?q={urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Libro.fm search")
    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(8000)

    result = LibroResult(query=request.search_query)

    checkpoint("Extract audiobook listings")
    js_code = """(max) => {
        const results = [];
        // Get all text and split by "Show audiobook details" marker
        const body = document.body.innerText;
        const parts = body.split('Show audiobook details');
        // Skip first part (nav/header content). Each subsequent part ends with "Title\\nAuthor"
        for (let i = 1; i < parts.length - 1 && results.length < max; i++) {
            const lines = parts[i].trim().split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            if (lines.length < 2) continue;
            const author = lines[lines.length - 1];
            const title = lines[lines.length - 2];
            // Skip nav/header/promo text
            if (!title || title.length < 3) continue;
            if (/Sort|Search by|Relevance|Shop the sale|Explore audio|membership/i.test(title)) continue;
            if (/Sort|Search by|Relevance|Shop the sale|Explore audio|membership/i.test(author)) continue;
            results.push({ title, author });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = AudiobookItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} audiobooks for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Author: {item.author}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("libro")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_libro_audiobooks(page, LibroRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} audiobooks")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
