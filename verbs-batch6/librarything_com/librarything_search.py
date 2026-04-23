"""
Auto-generated Playwright script (Python)
LibraryThing – Book Search
Query: "science fiction dystopia"

Generated on: 2026-04-18T14:46:45.636Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BookRequest:
    query: str = "science fiction dystopia"
    max_results: int = 5


@dataclass
class Book:
    title: str = ""
    author: str = ""
    rating: str = ""
    members: str = ""
    url: str = ""


@dataclass
class BookResult:
    books: List[Book] = field(default_factory=list)


def librarything_search(page: Page, request: BookRequest) -> BookResult:
    """Search LibraryThing for books."""
    print(f"  Query: {request.query}\n")

    # LibraryThing search requires login and/or hits Cloudflare, use Google site search
    from urllib.parse import quote_plus
    url = f"https://www.google.com/search?q=site%3Alibrarything.com+{quote_plus(request.query)}+books"
    print(f"Loading {url}...")
    checkpoint("Navigate to Google site search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Scroll to load content
    for _ in range(3):
        page.evaluate("window.scrollBy(0, 600)")
        page.wait_for_timeout(800)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    checkpoint("Extract book results")
    books_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();
        const text = document.body.innerText;

        // Pattern: "N · Title · Author" from LibraryThing list snippets in Google
        // The format in snippets is: "1 · Fahrenheit 451 · Ray Bradbury ; 2 · 1984 · George Orwell"
        const bookPat = /\d+\s*·\s*([^·;]{3,80})\s*·\s*([^·;]{3,50})/g;
        let m;
        while ((m = bookPat.exec(text)) !== null) {
            if (results.length >= maxResults) break;
            let title = m[1].trim();
            let author = m[2].trim();
            // Skip date lines, nav items
            if (/^\d{4}|^(search|sign|log|menu|home|all|images|videos|news|more|tools|shopping|read more)/i.test(title)) continue;
            if (/^(search|sign|log|menu|home|all|images)/i.test(author)) continue;
            if (seen.has(title)) continue;
            seen.add(title);
            results.push({ title: title.slice(0, 120), author: author.slice(0, 60), rating: '', members: '', url: '' });
        }

        // Fallback: look for Google result headings with book-like content
        if (results.length === 0) {
            const h3s = document.querySelectorAll('h3');
            for (const h of h3s) {
                if (results.length >= maxResults) break;
                let t = h.innerText.trim();
                t = t.replace(/\s*[\|–—-]\s*LibraryThing.*$/i, '').trim();
                if (t.length < 5 || seen.has(t)) continue;
                if (/^(search|sign|log|menu|home)/i.test(t)) continue;
                seen.add(t);
                results.push({ title: t.slice(0, 120), author: '', rating: '', members: '', url: '' });
            }
        }
        return results;
    }""", request.max_results)

    books = [Book(**b) for b in books_data]

    result = BookResult(books=books[:request.max_results])

    print("\n" + "=" * 60)
    print(f"LibraryThing: {request.query}")
    print("=" * 60)
    for i, b in enumerate(result.books, 1):
        print(f"  {i}. {b.title}")
        if b.author:
            print(f"     Author:  {b.author}")
        if b.rating:
            print(f"     Rating:  {b.rating}")
        if b.members:
            print(f"     Members: {b.members}")
        if b.url:
            print(f"     URL:     {b.url}")
    print(f"\nTotal: {len(result.books)} books")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("librarything_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = librarything_search(page, BookRequest())
            print(f"\nReturned {len(result.books)} books")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
