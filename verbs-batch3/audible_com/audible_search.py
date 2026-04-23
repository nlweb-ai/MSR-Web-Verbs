"""
Playwright script (Python) — Audible.com Audiobook Search
Query: science fiction
Max results: 5

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
class AudibleSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class AudibleAudiobook:
    title: str
    author: str
    narrator: str
    length: str
    rating: str


@dataclass(frozen=True)
class AudibleSearchResult:
    query: str
    audiobooks: list[AudibleAudiobook]


# Searches Audible for audiobooks matching the given query and returns up to max_results
# audiobooks with title, author, narrator, length, and rating.
def search_audible_audiobooks(
    page: Page,
    request: AudibleSearchRequest,
) -> AudibleSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    results: list[AudibleAudiobook] = []

    try:
        # ── Navigate to search results ────────────────────────────────────
        search_query = query.replace(" ", "+")
        search_url = f"https://www.audible.com/search?keywords={search_query}"
        print(f"Loading {search_url}...")
        checkpoint(f"Navigate to {search_url}")
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)
        print(f"  Loaded: {page.url}")

        # ── Extract audiobooks ────────────────────────────────────────────
        print(f"Extracting up to {max_results} audiobooks...")

        product_items = page.locator("li.productListItem")
        count = product_items.count()
        print(f"  Found {count} product items on page")

        for i in range(min(count, max_results)):
            item = product_items.nth(i)
            try:
                text = item.inner_text(timeout=3000)

                title = item.get_attribute("aria-label", timeout=2000) or "N/A"

                author = "N/A"
                m = re.search(r"By:\s*(.+?)\n", text)
                if m:
                    author = m.group(1).strip()

                narrator = "N/A"
                m = re.search(r"Narrated by:\s*(.+?)\n", text)
                if m:
                    narrator = m.group(1).strip()

                length = "N/A"
                m = re.search(r"Length:\s*(.+?)\n", text)
                if m:
                    length = m.group(1).strip()

                rating = "N/A"
                m = re.search(r"(\d+\.\d+)\s*\n?\s*\d+\s*ratings?", text)
                if m:
                    rating = m.group(1)

                if title == "N/A":
                    continue

                results.append(AudibleAudiobook(
                    title=title,
                    author=author,
                    narrator=narrator,
                    length=length,
                    rating=rating,
                ))
            except Exception:
                continue

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nFound {len(results)} audiobooks for '{query}':\n")
        for i, book in enumerate(results, 1):
            print(f"  {i}. {book.title}")
            print(f"     Author: {book.author}")
            print(f"     Narrator: {book.narrator}")
            print(f"     Length: {book.length}")
            print(f"     Rating: {book.rating}")
            print()

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return AudibleSearchResult(
        query=query,
        audiobooks=results,
    )


def test_search_audible_audiobooks() -> None:
    request = AudibleSearchRequest(
        query="science fiction",
        max_results=5,
    )

    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=False,
            viewport=None,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_audible_audiobooks(page, request)
            assert result.query == request.query
            assert len(result.audiobooks) <= request.max_results
            print(f"\nTotal audiobooks found: {len(result.audiobooks)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_audible_audiobooks)
