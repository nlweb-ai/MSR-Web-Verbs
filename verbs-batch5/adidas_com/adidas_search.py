"""
Auto-generated Playwright script (Python)
adidas.com – Product Search
Search: running shoes

Generated on: 2026-04-17T23:18:16.513Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from playwright.sync_api import Playwright, sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class AdidasSearchRequest:
    search_term: str = "running shoes"
    max_results: int = 5


@dataclass(frozen=True)
class AdidasProduct:
    product_name: str = ""
    url: str = ""


@dataclass(frozen=True)
class AdidasSearchResult:
    products: list = None  # list[AdidasProduct]


def adidas_search(page: Page, request: AdidasSearchRequest) -> AdidasSearchResult:
    """Search adidas.com for products matching a search term and extract
    product name, price, color, rating, and number of reviews."""
    search_term = request.search_term
    max_results = request.max_results
    print(f"  Search term: {search_term}")
    print(f"  Max results: {max_results}\n")

    # ── Navigate to search results ────────────────────────────────────
    search_url = f"https://www.adidas.com/us/search?q={search_term.replace(' ', '+')}"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to adidas search")
    page.goto(search_url, wait_until="domcontentloaded")

    # Wait for product cards (article elements) to appear
    try:
        page.locator("article").first.wait_for(state="attached", timeout=15000)
    except Exception:
        pass

    # Dismiss loading screen overlay
    try:
        page.locator('[data-auto-id="loading-screen"]').wait_for(state="hidden", timeout=8000)
    except Exception:
        pass
    page.wait_for_timeout(2000)
    print(f"  Loaded: {page.url}")

    # ── Dismiss cookie / consent banners ──────────────────────────────
    for selector in [
        "button#onetrust-accept-btn-handler",
        'button:has-text("Accept")',
        'button:has-text("Accept All Cookies")',
    ]:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=1500):
                btn.evaluate("el => el.click()")
                page.wait_for_timeout(500)
                break
        except Exception:
            pass

    # ── Extract product listing data from article cards ───────────────
    checkpoint("Extract product listings from search results")
    articles = page.locator("main article")
    count = articles.count()
    print(f"  Found {count} product cards")

    listing_data = []

    for i in range(min(count, max_results)):
        card = articles.nth(i)
        try:
            # Product name: from the first link's alt text or text content
            name = "N/A"
            try:
                img_el = card.locator("a img").first
                name = (img_el.get_attribute("alt") or "").strip()
            except Exception:
                pass
            if name == "N/A":
                try:
                    name = (card.locator("a").first.text_content(timeout=2000) or "").strip()
                except Exception:
                    pass

            # Product URL
            url = ""
            try:
                url = card.locator("a").first.get_attribute("href") or ""
                if url and not url.startswith("http"):
                    url = f"https://www.adidas.com{url}"
            except Exception:
                pass

            if name == "N/A":
                continue
            listing_data.append((name, url))
        except Exception:
            continue

    print(f"  Collected {len(listing_data)} products from listing")

    results = []
    for name, url in listing_data:
        results.append(AdidasProduct(
            product_name=name,
            url=url,
        ))

    # ── Print results ─────────────────────────────────────────────────
    print("=" * 60)
    print(f'adidas - Search Results for "{search_term}"')
    print("=" * 60)
    for idx, p in enumerate(results, 1):
        print(f"\n{idx}. {p.product_name}")
        print(f"   URL: {p.url}")

    print(f"\nFound {len(results)} products")
    return AdidasSearchResult(products=results)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("adidas_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = adidas_search(page, AdidasSearchRequest())
            print(f"\nReturned {len(result.products or [])} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
