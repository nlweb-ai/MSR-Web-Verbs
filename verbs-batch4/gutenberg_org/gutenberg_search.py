"""
Project Gutenberg – Book Search (typed verb)

Uses Playwright via CDP connection with the user's Chrome profile.
"""

import os, sys, shutil, re
from dataclasses import dataclass
from urllib.parse import quote
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

@dataclass(frozen=True)
class GutenbergSearchRequest:
    query: str = "frankenstein"
    max_results: int = 5

@dataclass(frozen=True)
class GutenbergBook:
    title: str
    author: str
    ebook_id: str
    download_count: int
    detail_url: str

@dataclass(frozen=True)
class GutenbergSearchResult:
    query: str
    books: list[GutenbergBook]

# Searches the Project Gutenberg ebook catalog for a given query and returns
# up to max_results books. Each book has a title, author, ebook ID, download
# count, and detail page URL.
def search_gutenberg_books(
    page: Page,
    request: GutenbergSearchRequest,
) -> GutenbergSearchResult:
    query = request.query
    max_results = request.max_results
    print(f"  Query:       {query}")
    print(f"  Max results: {max_results}\n")

    search_url = f"https://www.gutenberg.org/ebooks/search/?query={quote(query)}"
    print(f"Loading search: {search_url}")
    page.goto(search_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_selector("li.booklink", timeout=10000)
    page.wait_for_timeout(2000)

    booklinks = page.locator("li.booklink")
    total = min(booklinks.count(), max_results)
    print(f"  Found {booklinks.count()} book results; extracting top {total}.")

    books: list[GutenbergBook] = []

    for i in range(total):
        li = booklinks.nth(i)

        anchor = li.locator('a.link[href^="/ebooks/"]').first
        href = anchor.get_attribute("href") or ""
        m = re.search(r"/ebooks/(\d+)", href)
        ebook_id = m.group(1) if m else ""
        detail_url = f"https://www.gutenberg.org{href}" if href else ""

        title_el = li.locator(".title").first
        title = (
            title_el.inner_text(timeout=2000).strip() if title_el.count() > 0 else ""
        )

        subtitle_el = li.locator(".subtitle").first
        author = (
            subtitle_el.inner_text(timeout=2000).strip()
            if subtitle_el.count() > 0
            else ""
        )

        extra_el = li.locator(".extra").first
        extra_raw = (
            extra_el.inner_text(timeout=2000).strip() if extra_el.count() > 0 else ""
        )
        dm = re.search(r"(\d[\d,]*)", extra_raw)
        download_count = int(dm.group(1).replace(",", "")) if dm else 0

        books.append(
            GutenbergBook(
                title=title,
                author=author,
                ebook_id=ebook_id,
                download_count=download_count,
                detail_url=detail_url,
            )
        )

    print(f"\nTop {len(books)} Gutenberg results for '{query}':")
    for idx, b in enumerate(books, 1):
        print(f"\n  [{idx}] {b.title}")
        print(f"      Author:     {b.author}")
        print(f"      Ebook ID:   {b.ebook_id}")
        print(f"      Downloads:  {b.download_count:,}")
        print(f"      Detail URL: {b.detail_url}")

    return GutenbergSearchResult(query=query, books=books)

def test_search_gutenberg_books() -> None:
    """Concrete test: search Gutenberg for 'frankenstein' and return top 5."""
    request = GutenbergSearchRequest(query="frankenstein", max_results=5)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        try:
            page = browser.new_page()
            result = search_gutenberg_books(page, request)

            assert isinstance(result, GutenbergSearchResult)
            assert result.query == request.query
            assert len(result.books) == request.max_results
            for b in result.books:
                assert isinstance(b, GutenbergBook)
                assert b.title
                assert b.ebook_id.isdigit()
                assert b.detail_url.startswith("https://www.gutenberg.org/ebooks/")
                assert b.download_count >= 0

            print("\n--- Test passed ---")
            print(f"  Retrieved {len(result.books)} typed GutenbergBook objects.")
        finally:
            try:
                browser.close()
            except Exception:
                pass

if __name__ == "__main__":
    test_search_gutenberg_books()
