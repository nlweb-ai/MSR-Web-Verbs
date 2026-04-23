import re
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class OverstockSearchRequest:
    query: str = "sectional sofa"
    max_results: int = 5

@dataclass(frozen=True)
class OverstockProduct:
    product_name: str = ""
    price: str = ""
    original_price: str = ""

@dataclass(frozen=True)
class OverstockSearchResult:
    products: list = None  # list[OverstockProduct]

# Search for products on Overstock.com homepage and extract details.
def overstock_search(page: Page, request: OverstockSearchRequest) -> OverstockSearchResult:
    query = request.query
    max_results = request.max_results
    print(f"  Search query: {query}")
    print(f"  Max results: {max_results}\n")

    # Overstock blocks search results and category pages ("Access Denied").
    # Only the homepage loads, so we extract featured products from it.
    url = "https://www.overstock.com"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to Overstock")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""

    results = []

    # Extract products from homepage body text.
    # Pattern: "X% Off" → "$price" → "product name" (repeating)
    text_lines = [l.strip() for l in body_text.split("\n") if l.strip()]

    i = 0
    while i < len(text_lines) and len(results) < max_results:
        line = text_lines[i]
        # Look for a price line as anchor
        pm = re.match(r'^\$([\d,]+\.?\d*)$', line)
        if pm:
            price = "$" + pm.group(1)
            product_name = "N/A"
            original_price = "N/A"
            discount = "N/A"

            # Product name is the next line
            if i + 1 < len(text_lines):
                next_line = text_lines[i + 1]
                # Skip if next line is another price or discount
                if not re.match(r'^[\d%$]', next_line) and len(next_line) > 5:
                    product_name = next_line

            # Discount is the line before the price
            if i > 0:
                prev = text_lines[i - 1]
                dm = re.match(r'^(\d+%)\s*Off$', prev)
                if dm:
                    discount = dm.group(1)

            # Filter: match query keywords if provided
            if product_name != "N/A":
                query_words = query.lower().split()
                name_lower = product_name.lower()
                if any(w in name_lower for w in query_words) or not query:
                    results.append(OverstockProduct(
                        product_name=product_name,
                        price=price,
                        original_price=discount + " off" if discount != "N/A" else "N/A",
                    ))
            i += 2
            continue
        i += 1

    # If no query matches, return all found products up to max
    if not results:
        print(f"  No products matching '{query}', returning featured products...")
        i = 0
        while i < len(text_lines) and len(results) < max_results:
            line = text_lines[i]
            pm = re.match(r'^\$([\d,]+\.?\d*)$', line)
            if pm:
                price = "$" + pm.group(1)
                product_name = "N/A"
                discount = "N/A"

                if i + 1 < len(text_lines):
                    next_line = text_lines[i + 1]
                    if not re.match(r'^[\d%$]', next_line) and len(next_line) > 5:
                        product_name = next_line

                if i > 0:
                    prev = text_lines[i - 1]
                    dm = re.match(r'^(\d+%)\s*Off$', prev)
                    if dm:
                        discount = dm.group(1)

                if product_name != "N/A":
                    results.append(OverstockProduct(
                        product_name=product_name,
                        price=price,
                        original_price=discount + " off" if discount != "N/A" else "N/A",
                    ))
                i += 2
                continue
            i += 1

    print("=" * 60)
    print(f"Overstock - Search Results for \"{query}\"")
    print("=" * 60)
    for idx, p in enumerate(results, 1):
        print(f"\n{idx}. {p.product_name}")
        print(f"   Price: {p.price}")
        print(f"   Original Price: {p.original_price}")

    print(f"\nFound {len(results)} products")

    return OverstockSearchResult(products=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = overstock_search(page, OverstockSearchRequest())
        print(f"\nReturned {len(result.products or [])} products")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
