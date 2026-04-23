"""
Playwright script (Python) — Goodreads Author Books
Search for an author and extract their top rated books.

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GoodreadsAuthorRequest:
    author: str
    max_results: int


@dataclass(frozen=True)
class GoodreadsBook:
    title: str
    avg_rating: str
    num_ratings: str


@dataclass(frozen=True)
class GoodreadsAuthorResult:
    author: str
    books: list[GoodreadsBook]


# Searches Goodreads for an author and extracts up to max_results
# of their top rated books with title, average rating, and number of ratings.
def search_goodreads_author(
    page: Page,
    request: GoodreadsAuthorRequest,
) -> GoodreadsAuthorResult:
    author = request.author
    max_results = request.max_results

    print(f"  Author: {author}")
    print(f"  Max results: {max_results}\n")

    results: list[GoodreadsBook] = []

    try:
        print(f'Loading Goodreads search for "{author}"...')
        url = f"https://www.goodreads.com/search?q={author.replace(' ', '+')}"
        checkpoint(f"Navigate to {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        print(f"STEP 1: Extract up to {max_results} top books...")

        rows = page.locator('tr[itemtype*="Book"]')
        count = rows.count()
        print(f"  Found {count} book rows")

        for i in range(min(count, max_results)):
            row = rows.nth(i)
            try:
                title = "N/A"
                avg_rating = "N/A"
                num_ratings = "N/A"
                try:
                    title_el = row.locator('a[class*="bookTitle"]').first
                    title = title_el.inner_text(timeout=2000).strip()
                except Exception:
                    pass
                try:
                    mini = row.locator('span[class*="minirating"]').first
                    mini_text = mini.inner_text(timeout=2000).strip()
                    m = re.match(r"([\d.]+)\s+avg rating\s*[—–-]\s*([\d,]+)\s+ratings", mini_text)
                    if m:
                        avg_rating = m.group(1)
                        num_ratings = m.group(2)
                except Exception:
                    pass
                if title != "N/A":
                    results.append(GoodreadsBook(title=title, avg_rating=avg_rating, num_ratings=num_ratings))
                    print(f"  {len(results)}. {title} | Rating: {avg_rating} | Ratings: {num_ratings}")
            except Exception as e:
                print(f"  Error on row {i}: {e}")

        print(f"\nTop {len(results)} books by '{author}':")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.title}")
            print(f"     Avg Rating: {r.avg_rating}  Num Ratings: {r.num_ratings}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return GoodreadsAuthorResult(author=author, books=results)


def test_search_goodreads_author() -> None:
    request = GoodreadsAuthorRequest(author="Isaac Asimov", max_results=5)
    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir, channel="chrome", headless=False, viewport=None,
            args=["--disable-blink-features=AutomationControlled", "--disable-infobars", "--disable-extensions"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_goodreads_author(page, request)
            assert result.author == request.author
            assert len(result.books) <= request.max_results
            print(f"\nTotal books found: {len(result.books)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_goodreads_author)
