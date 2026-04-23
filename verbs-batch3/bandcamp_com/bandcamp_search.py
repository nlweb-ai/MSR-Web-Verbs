"""
Playwright script (Python) — Bandcamp.com Album Search
Query: jazz
Max results: 5

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
from urllib.parse import quote_plus
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BandcampSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class BandcampAlbum:
    title: str
    artist: str
    price: str
    tags: str


@dataclass(frozen=True)
class BandcampSearchResult:
    query: str
    albums: list[BandcampAlbum]


# Searches Bandcamp for albums matching the given query and returns up to max_results
# albums with title, artist, price, and genre tags.
def search_bandcamp_albums(
    page: Page,
    request: BandcampSearchRequest,
) -> BandcampSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    results: list[BandcampAlbum] = []

    try:
        # ── Navigate to search results (item_type=a for albums) ──────────
        search_url = f"https://bandcamp.com/search?q={quote_plus(query)}&item_type=a"
        print(f"Loading {search_url}...")
        checkpoint(f"Navigate to {search_url}")
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)
        print(f"  Loaded: {page.url}")

        # ── Extract albums ────────────────────────────────────────────────
        print(f"Extracting up to {max_results} albums...")

        result_items = page.locator("li.searchresult")
        count = result_items.count()
        print(f"  Found {count} search results")

        for i in range(min(count, max_results)):
            item = result_items.nth(i)
            try:
                title = "N/A"
                try:
                    title_el = item.locator(".heading").first
                    title = title_el.inner_text(timeout=3000).strip()
                except Exception:
                    pass

                artist = "N/A"
                try:
                    subhead_el = item.locator(".subhead").first
                    subhead_text = subhead_el.inner_text(timeout=3000).strip()
                    artist = re.sub(r"^by\s+", "", subhead_text).strip()
                except Exception:
                    pass

                tags = "N/A"
                try:
                    tags_el = item.locator(".tags").first
                    tags_text = tags_el.inner_text(timeout=3000).strip()
                    tags = re.sub(r"^tags:\s*", "", tags_text).strip()
                except Exception:
                    pass

                price = "N/A"
                try:
                    item_text = item.inner_text(timeout=3000)
                    m = re.search(r"(\$[\d.]+|\xA3[\d.]+|\u20AC[\d.]+|name your price|free)", item_text, re.IGNORECASE)
                    if m:
                        price = m.group(1)
                except Exception:
                    pass

                if title == "N/A":
                    continue

                results.append(BandcampAlbum(
                    title=title,
                    artist=artist,
                    price=price,
                    tags=tags,
                ))
            except Exception:
                continue

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nFound {len(results)} albums for '{query}':\n")
        for i, album in enumerate(results, 1):
            print(f"  {i}. {album.title}")
            print(f"     Artist: {album.artist}")
            print(f"     Price: {album.price}")
            print(f"     Tags: {album.tags}")
            print()

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return BandcampSearchResult(
        query=query,
        albums=results,
    )


def test_search_bandcamp_albums() -> None:
    request = BandcampSearchRequest(
        query="jazz",
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
            result = search_bandcamp_albums(page, request)
            assert result.query == request.query
            assert len(result.albums) <= request.max_results
            print(f"\nTotal albums found: {len(result.albums)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_bandcamp_albums)
