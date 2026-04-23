"""
Playwright script (Python) — Sephora Product Search
Search for beauty products and extract name, brand, price, and rating.

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
class SephoraSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class SephoraProduct:
    name: str
    brand: str
    price: str
    rating: str


@dataclass(frozen=True)
class SephoraSearchResult:
    query: str
    products: list[SephoraProduct]


# Searches Sephora for beauty products matching a query, then extracts
# up to max_results products with name, brand, price, and rating.
def search_sephora(
    page: Page,
    request: SephoraSearchRequest,
) -> SephoraSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}\n")

    results: list[SephoraProduct] = []

    try:
        search_url = f"https://www.sephora.com/search?keyword={urllib.parse.quote(query)}"
        checkpoint(f"Navigate to {search_url}")
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)

        body_text = page.locator("body").inner_text(timeout=5000)
        lines = [l.strip() for l in body_text.split("\n") if l.strip()]
        i = 0
        while i < len(lines) and len(results) < max_results:
            if lines[i] == "Quicklook" and i + 3 < len(lines):
                brand = lines[i + 1]
                name = lines[i + 2]
                if "$" in brand or len(brand) > 60:
                    i += 1
                    continue
                price = "N/A"
                rating = "N/A"
                for j in range(i + 3, min(i + 6, len(lines))):
                    if "$" in lines[j] and price == "N/A":
                        price = lines[j]
                    if re.match(r"[\d.]+K?$", lines[j]):
                        rating = lines[j]
                results.append(SephoraProduct(name=name, brand=brand, price=price, rating=rating))
                print(f"  {len(results)}. {name} | {brand} | {price} | {rating}")
                i += 5
            else:
                i += 1

        print(f"\nFound {len(results)} products:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name} — {r.brand} ({r.price}) [{r.rating}]")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return SephoraSearchResult(query=query, products=results)


def test_search_sephora() -> None:
    request = SephoraSearchRequest(query="moisturizer", max_results=5)
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
            result = search_sephora(page, request)
            assert result.query == request.query
            assert len(result.products) <= request.max_results
            print(f"\nTotal products found: {len(result.products)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_sephora)
