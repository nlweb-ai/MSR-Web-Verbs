"""
Playwright script (Python) — ASOS.com Product Search
Query: men's jackets
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
class AsosSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class AsosProduct:
    name: str
    price: str
    brand: str


@dataclass(frozen=True)
class AsosSearchResult:
    query: str
    products: list[AsosProduct]


# Searches ASOS for products matching the given query and returns up to max_results
# products with name, price, and brand.
def search_asos_products(
    page: Page,
    request: AsosSearchRequest,
) -> AsosSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    results: list[AsosProduct] = []

    try:
        # ── Navigate directly to search results ──────────────────────────
        search_query = query.replace(" ", "+")
        search_url = f"https://www.asos.com/search/?q={search_query}"
        print(f"Loading {search_url}...")
        checkpoint(f"Navigate to {search_url}")
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)
        print(f"  Loaded: {page.url}")

        # ── Extract products ──────────────────────────────────────────────
        print(f"Extracting up to {max_results} products...")

        product_cards = page.locator("li[id^='product-']")
        count = product_cards.count()
        print(f"  Found {count} product cards on page")

        for i in range(min(count, max_results)):
            card = product_cards.nth(i)
            try:
                link = card.locator("a[href*='/prd/']").first
                aria_label = link.get_attribute("aria-label", timeout=3000)
                href = link.get_attribute("href", timeout=3000) or ""

                name = "N/A"
                price = "N/A"
                brand = "N/A"

                if aria_label:
                    m = re.match(r"^(.+?),\s*Price\s+(.+)$", aria_label)
                    if m:
                        name = m.group(1).strip()
                        price = m.group(2).strip()

                if href:
                    brand_match = re.search(r"asos\.com/([^/]+)/", href)
                    if brand_match:
                        brand = brand_match.group(1).replace("-", " ").title()

                if name == "N/A":
                    continue

                results.append(AsosProduct(
                    name=name,
                    price=price,
                    brand=brand,
                ))
            except Exception:
                continue

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nFound {len(results)} products for '{query}':\n")
        for i, product in enumerate(results, 1):
            print(f"  {i}. {product.name}")
            print(f"     Brand: {product.brand}")
            print(f"     Price: {product.price}")
            print()

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return AsosSearchResult(
        query=query,
        products=results,
    )


def test_search_asos_products() -> None:
    request = AsosSearchRequest(
        query="men's jackets",
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
            result = search_asos_products(page, request)
            assert result.query == request.query
            assert len(result.products) <= request.max_results
            print(f"\nTotal products found: {len(result.products)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_asos_products)
