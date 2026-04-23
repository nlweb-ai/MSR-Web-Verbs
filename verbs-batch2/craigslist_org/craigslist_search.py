"""
Playwright script (Python) — Craigslist For Sale Search
Search for listings in the For Sale section and extract title, price, and location.

Uses the user's Chrome profile for persistent login state.
"""

import os
from urllib.parse import quote
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CraigslistSearchRequest:
    query: str
    region: str
    max_results: int


@dataclass(frozen=True)
class CraigslistListing:
    title: str
    price: str
    location: str


@dataclass(frozen=True)
class CraigslistSearchResult:
    query: str
    region: str
    listings: list[CraigslistListing]


# Searches Craigslist For Sale in a given region for a query and extracts
# up to max_results listings with title, price, and location.
def search_craigslist(
    page: Page,
    request: CraigslistSearchRequest,
) -> CraigslistSearchResult:
    query = request.query
    region = request.region
    max_results = request.max_results

    print(f"  Query: {query}")
    print(f"  Region: {region}")
    print(f"  Max results: {max_results}\n")

    results: list[CraigslistListing] = []

    try:
        # ── Navigate to search results ────────────────────────────────────
        url = f"https://{region}.craigslist.org/search/sss?query={quote(query)}#search=2~list~0"
        print(f"Loading {url}...")
        checkpoint(f"Navigate to {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)
        print(f"  URL: {page.url}")

        # ── Extract listings ──────────────────────────────────────────────
        print(f"Extracting up to {max_results} listings...")

        cards = page.locator(".cl-search-result")
        count = cards.count()
        print(f"  Found {count} listing cards")

        for i in range(min(count, max_results)):
            card = cards.nth(i)
            try:
                # Title
                title = "N/A"
                try:
                    title_el = card.locator("a.posting-title").first
                    title = title_el.inner_text(timeout=2000).strip()
                except Exception:
                    pass

                # Price
                price = "N/A"
                try:
                    price_el = card.locator("span.priceinfo").first
                    price = price_el.inner_text(timeout=2000).strip()
                except Exception:
                    pass

                # Location
                location = "N/A"
                try:
                    loc_el = card.locator("span.result-location").first
                    location = loc_el.inner_text(timeout=2000).strip()
                except Exception:
                    pass

                results.append(CraigslistListing(
                    title=title,
                    price=price,
                    location=location,
                ))

            except Exception as e:
                print(f"  Skipping card {i + 1}: {e}")

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nListings for '{query}' on {region}.craigslist.org:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.title}")
            print(f"     Price:    {r.price}")
            print(f"     Location: {r.location}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return CraigslistSearchResult(
        query=query,
        region=region,
        listings=results,
    )


def test_search_craigslist() -> None:
    request = CraigslistSearchRequest(
        query="bicycle",
        region="sfbay",
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
            result = search_craigslist(page, request)
            assert result.query == request.query
            assert result.region == request.region
            assert len(result.listings) <= request.max_results
            print(f"\nTotal listings found: {len(result.listings)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_craigslist)
