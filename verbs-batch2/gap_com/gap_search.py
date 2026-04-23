"""
Playwright script (Python) — Gap.com Product Search
Search for products matching a query, extract name, price, and available sizes.

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
class GapSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class GapProduct:
    name: str
    price: str
    sizes: str


@dataclass(frozen=True)
class GapSearchResult:
    query: str
    products: list[GapProduct]


# Searches Gap.com for products matching a query, then extracts
# up to max_results products with name, price, and available sizes.
def search_gap(
    page: Page,
    request: GapSearchRequest,
) -> GapSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    results: list[GapProduct] = []

    try:
        print("Loading Gap.com search results...")
        search_url = f"https://www.gap.com/browse/search.do?searchText={query.replace(' ', '+')}"
        checkpoint(f"Navigate to {search_url}")
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(4000)

        for selector in [
            "button#onetrust-accept-btn-handler",
            "button:has-text('Accept')",
            "button:has-text('Close')",
            "button[aria-label='close']",
        ]:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {selector}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        print(f'STEP 1: Extract up to {max_results} products for "{query}"...')

        h3s = page.locator("h3")
        count = h3s.count()
        print(f"  Found {count} product headings")

        for i in range(count):
            if len(results) >= max_results:
                break
            h3 = h3s.nth(i)
            try:
                name = h3.inner_text(timeout=2000).strip()
                if not name or len(name) < 3:
                    continue
                card_text = h3.evaluate(
                    "el => el.closest('div[class*=\"product-card\"]')?.innerText || el.parentElement.innerText"
                )
                price_match = re.search(r"\$[\d,.]+", card_text)
                price = price_match.group(0) if price_match else "N/A"
                results.append(GapProduct(name=name, price=price, sizes="N/A"))
                print(f"  {len(results)}. {name} | {price}")
            except Exception:
                continue

        print(f"\nFound {len(results)} products for '{query}':")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name}")
            print(f"     Price: {r.price}  Sizes: {r.sizes}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return GapSearchResult(query=query, products=results)


def test_search_gap() -> None:
    request = GapSearchRequest(query="men's jeans", max_results=5)
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
            result = search_gap(page, request)
            assert result.query == request.query
            assert len(result.products) <= request.max_results
            print(f"\nTotal products found: {len(result.products)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_gap)
