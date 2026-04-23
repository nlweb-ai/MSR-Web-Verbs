"""
Playwright script (Python) — AbeBooks Used/Rare Book Search
Search for books and extract listing details.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class AbeBooksSearchRequest:
    search_query: str = "To Kill a Mockingbird first edition"
    max_results: int = 5


@dataclass
class BookListingItem:
    title: str = ""
    author: str = ""
    edition: str = ""
    condition: str = ""
    seller: str = ""
    price: str = ""


@dataclass
class AbeBooksSearchResult:
    query: str = ""
    items: List[BookListingItem] = field(default_factory=list)


# Searches AbeBooks for books matching a query and extracts listing details
# including title, author, edition, condition, seller, and price.
def search_abebooks(page: Page, request: AbeBooksSearchRequest) -> AbeBooksSearchResult:
    """Search AbeBooks for book listings."""
    print(f"  Query: {request.search_query}\n")

    encoded = quote_plus(request.search_query)
    url = f"https://www.abebooks.com/servlet/SearchResults?kn={encoded}&sortby=17"
    print(f"Loading {url}...")
    checkpoint("Navigate to AbeBooks search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Dismiss cookie/popup
    for sel in ['button:has-text("Accept")', '#onetrust-accept-btn-handler', 'button:has-text("Got it")']:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.evaluate("el => el.click()")
                page.wait_for_timeout(500)
        except Exception:
            pass

    result = AbeBooksSearchResult(query=request.search_query)

    checkpoint("Extract book listings")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('[data-cy="listing-item"], .result-item, [id^="book-"], .cf.result');
        for (const card of cards) {
            if (items.length >= max) break;
            const text = (card.textContent || '').replace(/\\s+/g, ' ').trim();

            let title = '';
            const titleEl = card.querySelector('[data-cy="listing-title"], h2, .title a, .result-title a');
            if (titleEl) title = titleEl.textContent.trim();

            let author = '';
            const authorEl = card.querySelector('[data-cy="listing-author"], .author, .by-author');
            if (authorEl) author = authorEl.textContent.replace(/^by\\s*/i, '').trim();

            let edition = '';
            const edMatch = text.match(/(first edition|\\d+(?:st|nd|rd|th)\\s+edition|edition:\\s*\\w+)/i);
            if (edMatch) edition = edMatch[1];

            let condition = '';
            const condEl = card.querySelector('[data-cy="listing-condition"], .condition');
            if (condEl) condition = condEl.textContent.trim();
            if (!condition) {
                const condMatch = text.match(/(hardcover|softcover|paperback|fine|good|fair|poor|new|used)/i);
                if (condMatch) condition = condMatch[1];
            }

            let seller = '';
            const sellerEl = card.querySelector('[data-cy="listing-bookseller"], .bookseller a, .seller a');
            if (sellerEl) seller = sellerEl.textContent.trim();
            if (!seller) {
                const sellerMatch = text.match(/Seller:\\s*([^(]+)/);
                if (sellerMatch) seller = sellerMatch[1].trim();
            }

            let price = '';
            const priceEl = card.querySelector('[data-cy="listing-price"], .item-price, .srp-item-price');
            if (priceEl) price = priceEl.textContent.trim();
            if (!price) {
                const pm = text.match(/(US\\$|\\$|£|€)[\\d,.]+/);
                if (pm) price = pm[0];
            }

            if (title) {
                items.push({title, author, edition, condition, seller, price});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = BookListingItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.edition = d.get("edition", "")
        item.condition = d.get("condition", "")
        item.seller = d.get("seller", "")
        item.price = d.get("price", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} listings for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Author:    {item.author}")
        print(f"     Edition:   {item.edition}")
        print(f"     Condition: {item.condition}")
        print(f"     Seller:    {item.seller}")
        print(f"     Price:     {item.price}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("abebooks")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = AbeBooksSearchRequest()
            result = search_abebooks(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} listings")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
