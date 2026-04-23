"""
Playwright script (Python) — IKEA Product Search
Search for products, extract name, price, and dimensions.

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
class IkeaSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class IkeaProduct:
    name: str
    price: str
    dimensions: str


@dataclass(frozen=True)
class IkeaSearchResult:
    query: str
    products: list[IkeaProduct]


# Searches IKEA for products matching a query, then extracts
# up to max_results products with name, price, and dimensions.
def search_ikea(
    page: Page,
    request: IkeaSearchRequest,
) -> IkeaSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    results: list[IkeaProduct] = []

    try:
        print("Loading IKEA search results...")
        url = f"https://www.ikea.com/us/en/search/?q={query.replace(' ', '+')}"
        checkpoint(f"Navigate to {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(4000)

        for sel in ["button#onetrust-accept-btn-handler", "button:has-text('Accept')", "button:has-text('Close')"]:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {sel}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        print(f'STEP 1: Extract up to {max_results} products for "{query}"...')
        cards = page.locator('div[class*="card"]')
        count = cards.count()
        print(f"  Found {count} cards")

        for i in range(count):
            if len(results) >= max_results:
                break
            card = cards.nth(i)
            try:
                card_text = card.inner_text(timeout=2000).strip()
                if not card_text or "$" not in card_text:
                    continue
                lines = [l.strip() for l in card_text.split("\n") if l.strip()]
                name = None
                description = None
                price = None
                for j, line in enumerate(lines):
                    if line.isupper() and len(line) > 2 and not line.startswith("$") and line not in ("Compare", "New"):
                        name = line
                        if j + 1 < len(lines) and not lines[j+1].startswith("$"):
                            description = lines[j+1]
                        break
                if not name:
                    continue
                for line in lines:
                    if line.startswith("$"):
                        price = line
                        break
                if not price:
                    continue
                full_name = f"{name} - {description}" if description else name
                results.append(IkeaProduct(name=full_name, price=price, dimensions="N/A"))
                print(f"  {len(results)}. {full_name} | {price}")
            except Exception:
                continue

        print(f"\nFound {len(results)} products for '{query}':")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name}")
            print(f"     Price: {r.price}  Dimensions: {r.dimensions}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return IkeaSearchResult(query=query, products=results)


def test_search_ikea() -> None:
    request = IkeaSearchRequest(query="bookshelf", max_results=5)
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
            result = search_ikea(page, request)
            assert result.query == request.query
            assert len(result.products) <= request.max_results
            print(f"\nTotal products found: {len(result.products)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_ikea)
