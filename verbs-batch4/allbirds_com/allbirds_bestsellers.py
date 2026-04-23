"""
Playwright script (Python) — Allbirds Best Sellers

Navigates to the Allbirds Best Sellers collection page and extracts the top N
most popular items with name, product handle, current price, compare-at price,
and detail page URL.

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
import sys
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class AllbirdsBestSellersRequest:
    max_results: int

@dataclass(frozen=True)
class AllbirdsProduct:
    name: str
    handle: str
    current_price: str
    compare_at_price: str  # empty string if not on sale
    detail_url: str

@dataclass(frozen=True)
class AllbirdsBestSellersResult:
    products: list[AllbirdsProduct]

# Retrieves the most popular (best-selling) items from the Allbirds Best Sellers
# collection page. For each product, extracts the name, product handle (URL slug),
# current price, compare-at (original) price when on sale, and detail page URL.
def get_allbirds_best_sellers(
    page: Page,
    request: AllbirdsBestSellersRequest,
) -> AllbirdsBestSellersResult:
    max_results = request.max_results
    print(f"  Max results: {max_results}\n")

    url = "https://www.allbirds.com/collections/best-sellers"
    print(f"Loading: {url}")
    checkpoint("Navigate to https://www.allbirds.com/collections/best-sellers")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    # Product anchors are in the DOM before they scroll into view; wait for
    # attached state rather than visible to avoid lazy-render timeouts.
    page.wait_for_selector('a[href^="/products/"]', timeout=15000, state="attached")
    page.wait_for_timeout(2000)

    # Trigger lazy-load by scrolling through the grid until anchor count stabilizes.
    checkpoint("Scroll to lazy-load product grid")
    prev_count = 0
    for _ in range(6):
        cur = page.locator('a[href^="/products/"]').count()
        if cur == prev_count and cur >= max_results * 2:
            break
        prev_count = cur
        page.evaluate("window.scrollBy(0, 1500)")
        page.wait_for_timeout(1200)
    # Scroll back to top so any "above the fold" lazy images also render.
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(800)

    anchors = page.locator('a[href^="/products/"]')
    total_on_page = anchors.count()
    print(f"  Found {total_on_page} product anchors on the page.")

    products: list[AllbirdsProduct] = []
    seen_handles: set[str] = set()

    checkpoint(f"Extract up to {max_results} product cards")
    for i in range(total_on_page):
        if len(products) >= max_results:
            break
        card = anchors.nth(i)

        href = card.get_attribute("href") or ""
        # Skip carousel/module cards whose href carries tracking query params;
        # real grid cards have a clean /products/<handle> path.
        if "?" in href:
            continue
        m = re.match(r"^/products/([a-z0-9\-]+)$", href)
        if not m:
            continue
        handle = m.group(1)
        if handle in seen_handles:
            continue
        detail_url = f"https://www.allbirds.com{href}"

        # Product name — primary source: the img[alt] attribute (set for
        # accessibility). Fallback: title-case the handle if alt is missing.
        name = ""
        img = card.locator("img[alt]").first
        if img.count() > 0:
            alt = img.get_attribute("alt") or ""
            name = alt.strip()
        if not name:
            # Handle e.g. "mens-cruiser-canvas-auburn" → "Mens Cruiser Canvas Auburn"
            name = " ".join(w.capitalize() for w in handle.split("-"))
        seen_handles.add(handle)

        # Prices: collect all $-prefixed spans inside the card
        price_spans = card.locator("span").all()
        dollar_texts: list[str] = []
        strikethrough: list[str] = []
        for sp in price_spans:
            try:
                t = sp.inner_text(timeout=1500).strip()
            except Exception:
                continue
            if not t or "$" not in t:
                continue
            dollar_texts.append(t)
            cls = sp.get_attribute("class") or ""
            if "line-through" in cls:
                strikethrough.append(t)

        # De-dupe and parse
        if strikethrough:
            compare_at_price = strikethrough[0]
            # current price is the first non-strikethrough $ span
            current_price = next(
                (t for t in dollar_texts if t not in strikethrough),
                dollar_texts[-1] if dollar_texts else "",
            )
        else:
            compare_at_price = ""
            current_price = dollar_texts[0] if dollar_texts else ""

        products.append(
            AllbirdsProduct(
                name=name,
                handle=handle,
                current_price=current_price,
                compare_at_price=compare_at_price,
                detail_url=detail_url,
            )
        )

    # Print
    print(f"\nTop {len(products)} Allbirds best sellers:")
    for idx, p in enumerate(products, 1):
        price_str = p.current_price
        if p.compare_at_price:
            price_str = f"{p.current_price}  (was {p.compare_at_price})"
        print(f"\n  [{idx}] {p.name}")
        print(f"      Handle:     {p.handle}")
        print(f"      Price:      {price_str}")
        print(f"      Detail URL: {p.detail_url}")

    return AllbirdsBestSellersResult(products=products)

def test_get_allbirds_best_sellers() -> None:
    """Concrete test: fetch the top 5 Allbirds best sellers."""
    request = AllbirdsBestSellersRequest(max_results=5)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        try:
            result = get_allbirds_best_sellers(page, request)

            assert isinstance(result, AllbirdsBestSellersResult)
            assert 1 <= len(result.products) <= request.max_results, (
                f"expected 1..{request.max_results} products, got {len(result.products)}"
            )
            for p in result.products:
                assert isinstance(p, AllbirdsProduct)
                assert p.name, "empty product name"
                assert p.handle, "empty handle"
                assert p.detail_url.startswith("https://www.allbirds.com/products/")
                assert p.current_price.startswith("$") or p.current_price == "", (
                    f"unexpected price format: {p.current_price!r}"
                )

            print("\n--- Test passed ---")
            print(f"  Retrieved {len(result.products)} typed AllbirdsProduct objects.")
        finally:
            browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_get_allbirds_best_sellers)
