"""
Playwright script (Python) — Nordstrom Product Search
Search for products and extract name and price.

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
import urllib.parse
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class NordstromSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class NordstromProduct:
    name: str
    price: str


@dataclass(frozen=True)
class NordstromSearchResult:
    query: str
    products: list[NordstromProduct]


# Searches Nordstrom for products matching a query, then extracts
# up to max_results products with name and price.
def search_nordstrom(
    page: Page,
    request: NordstromSearchRequest,
) -> NordstromSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}\n")

    results: list[NordstromProduct] = []

    try:
        search_url = f"https://www.nordstrom.com/sr?keyword={urllib.parse.quote(query)}"
        checkpoint(f"Navigate to {search_url}")
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(4000)

        articles = page.locator("article")
        count = articles.count()

        for i in range(min(count, max_results)):
            card = articles.nth(i)
            name = price = "N/A"
            try:
                name = card.locator('h3').first.inner_text(timeout=2000).strip()
            except Exception:
                pass
            try:
                card_text = card.inner_text(timeout=2000)
                pm = re.search(r"\$[\d,.]+", card_text)
                price = pm.group(0) if pm else "N/A"
            except Exception:
                pass
            if name != "N/A":
                results.append(NordstromProduct(name=name, price=price))
                print(f"  {len(results)}. {name} | {price}")

        print(f"\nFound {len(results)} products:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name} ({r.price})")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return NordstromSearchResult(query=query, products=results)


def test_search_nordstrom() -> None:
    request = NordstromSearchRequest(query="men's dress shoes", max_results=5)
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
            result = search_nordstrom(page, request)
            assert result.query == request.query
            assert len(result.products) <= request.max_results
            print(f"\nTotal products found: {len(result.products)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_nordstrom)
