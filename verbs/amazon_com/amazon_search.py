"""
Amazon – Product Search
Pure Playwright – no AI.
"""
import re, os, sys, shutil, traceback
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

from dataclasses import dataclass


@dataclass(frozen=True)
class AmazonSearchRequest:
    query: str = "travel adapter worldwide"
    max_results: int = 5


@dataclass(frozen=True)
class AmazonProduct:
    name: str
    price: str
    rating: str


@dataclass(frozen=True)
class AmazonSearchResult:
    query: str
    products: list[AmazonProduct]
def search_amazon_products(page: Page, request: AmazonSearchRequest) -> AmazonSearchResult:
    products = []

    try:
        query_encoded = request.query.replace(" ", "+")
        url = f"https://www.amazon.com/s?k={query_encoded}&s=review-rank"
        print(f"STEP 1: Navigate to Amazon search for '{request.query}'...")
        checkpoint(f"Navigate to Amazon search: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(4000)

        # Dismiss popups
        for sel in ["#sp-cc-accept", "input[data-action-type='DISMISS']",
                    "button:has-text('Accept')"]:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=800):
                    checkpoint(f"Dismiss popup: {sel}")
                    loc.evaluate("el => el.click()")
                    page.wait_for_timeout(400)
            except Exception:
                pass

        # Scroll to load results
        for _ in range(3):
            checkpoint("Scroll down to load more results")
            page.evaluate("window.scrollBy(0, 600)")
            page.wait_for_timeout(700)

        print("STEP 2: Extract product cards...")
        seen = set()
        items = page.locator("[data-component-type='s-search-result']").all()
        print(f"   Found {len(items)} search result items")

        for item in items:
            if len(products) >= request.max_results:
                break
            try:
                # Name — h2 span holds the title directly in current Amazon markup
                name_el = item.locator("h2 span").first
                name = name_el.inner_text(timeout=1000).strip()
                # Skip HTML-tag garbage or too-short strings
                if not name or len(name) < 5 or re.search(r'</?\w+>', name):
                    continue
                key = name.lower()[:60]
                if key in seen:
                    continue
                seen.add(key)

                # Price
                price = "N/A"
                try:
                    price = item.locator(".a-price .a-offscreen").first.inner_text(timeout=800).strip()
                except Exception:
                    try:
                        price = item.locator(".a-price-whole").first.inner_text(timeout=800).strip()
                        if price:
                            price = "$" + price
                    except Exception:
                        pass

                # Rating
                rating = "N/A"
                try:
                    rating_txt = item.locator(".a-icon-alt").first.inner_text(timeout=800).strip()
                    m = re.search(r"([\d.]+) out of", rating_txt)
                    if m:
                        rating = m.group(1)
                except Exception:
                    pass

                products.append({"name": name, "price": price, "rating": rating})
            except Exception:
                continue

        print(f"\nDONE – {len(products)} products:")
        for i, p in enumerate(products, 1):
            print(f"  {i}. {p['name']}")
            print(f"     Price: {p['price']}  Rating: {p['rating']}")

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

    return AmazonSearchResult(
        query=request.query,
        products=[AmazonProduct(name=p['name'], price=p['price'], rating=p['rating']) for p in products],
    )


def test_amazon_products() -> None:
    request = AmazonSearchRequest(query="travel adapter worldwide", max_results=5)
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
            result = search_amazon_products(page, request)
            print(f"\nTotal products: {len(result.products)}")
            for i, p in enumerate(result.products, 1):
                print(f"  {i}. {p.name}  {p.price}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_amazon_products)
