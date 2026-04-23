"""
Playwright script (Python) — Walgreens Product Search
Search for products and extract name, price, and size.

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
class WalgreensSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class WalgreensProduct:
    name: str
    price: str
    size: str


@dataclass(frozen=True)
class WalgreensSearchResult:
    query: str
    products: list[WalgreensProduct]


# Searches Walgreens for products matching a query, then extracts
# up to max_results products with name, price, and size.
def search_walgreens(
    page: Page,
    request: WalgreensSearchRequest,
) -> WalgreensSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}\n")

    results: list[WalgreensProduct] = []

    try:
        search_url = f"https://www.walgreens.com/search/results.jsp?Ntt={urllib.parse.quote(query)}"
        checkpoint(f"Navigate to {search_url}")
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)

        cards = page.locator('div[class*="card__product"]')
        count = cards.count()

        for i in range(min(count, max_results)):
            card = cards.nth(i)
            name = price = size = "N/A"
            txt = card.inner_text(timeout=2000)
            lines = [l.strip() for l in txt.split("\n") if l.strip()]
            if lines:
                name = lines[0]
            for line in lines:
                m = re.search(r'\$\d+\.\d{2}', line)
                if m and price == "N/A":
                    price = m.group(0)
                    break
            if len(lines) > 1 and not lines[1].startswith("$") and not lines[1].startswith("("):
                size = lines[1]
            if name != "N/A":
                results.append(WalgreensProduct(name=name[:100], price=price, size=size))
                print(f"  {len(results)}. {name[:80]} | {price} | {size}")

        print(f"\nFound {len(results)} products:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name} — {r.price} ({r.size})")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return WalgreensSearchResult(query=query, products=results)


def test_search_walgreens() -> None:
    request = WalgreensSearchRequest(query="vitamin D", max_results=5)
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
            result = search_walgreens(page, request)
            assert result.query == request.query
            assert len(result.products) <= request.max_results
            print(f"\nTotal products found: {len(result.products)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_walgreens)
