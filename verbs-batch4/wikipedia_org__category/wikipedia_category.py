"""
Wikipedia – Category Page verb
Navigate to a Wikipedia category page and extract subcategories or page titles.
"""

import os
from dataclasses import dataclass
from playwright.sync_api import Page, sync_playwright

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

# ── Types ─────────────────────────────────────────────────────────────────────

@dataclass
class WikipediaCategoryRequest:
    category: str       # e.g. "Category:Programming languages"
    max_results: int    # number of items to extract

@dataclass
class WikipediaCategoryItem:
    title: str  # subcategory or page name
    type: str   # "subcategory" or "page"

@dataclass
class WikipediaCategoryResult:
    items: list  # list of WikipediaCategoryItem

# ── Verb ──────────────────────────────────────────────────────────────────────

def wikipedia_category(page: Page, request: WikipediaCategoryRequest) -> WikipediaCategoryResult:
    """
    Navigate to a Wikipedia category page and extract subcategories/pages.

    Args:
        page: Playwright page.
        request: WikipediaCategoryRequest with category and max_results.

    Returns:
        WikipediaCategoryResult containing a list of WikipediaCategoryItem.
    """
    cat_slug = request.category.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{cat_slug}"
    print(f"Loading {url}...")
    page.goto(url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)
    print(f"  Loaded: {page.url}")
    checkpoint("Loaded Wikipedia category page")

    results = []

    # Extract subcategories
    print("Extracting subcategories...")
    subcat_links = page.locator('#mw-subcategories .CategoryTreeItem a, #mw-subcategories li a')
    subcat_count = subcat_links.count()
    print(f"  Found {subcat_count} subcategory links")

    for i in range(subcat_count):
        if len(results) >= request.max_results:
            break
        try:
            title = subcat_links.nth(i).inner_text(timeout=2000).strip()
            if title:
                results.append(WikipediaCategoryItem(title=title, type="subcategory"))
        except Exception:
            pass

    # Extract pages
    if len(results) < request.max_results:
        print("Extracting pages...")
        page_links = page.locator('#mw-pages li a')
        page_count = page_links.count()
        print(f"  Found {page_count} page links")

        for i in range(page_count):
            if len(results) >= request.max_results:
                break
            try:
                title = page_links.nth(i).inner_text(timeout=2000).strip()
                if title:
                    results.append(WikipediaCategoryItem(title=title, type="page"))
            except Exception:
                pass

    checkpoint("Extracted category items")
    print(f"\nFound {len(results)} items in '{request.category}':")
    for i, item in enumerate(results, 1):
        print(f"  {i}. [{item.type}] {item.title}")

    return WikipediaCategoryResult(items=results)

# ── Test ──────────────────────────────────────────────────────────────────────

def test_func():

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()

        request = WikipediaCategoryRequest(category="Category:Programming languages", max_results=20)
        result = wikipedia_category(page, request)
        print(f"\nTotal items found: {len(result.items)}")

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
