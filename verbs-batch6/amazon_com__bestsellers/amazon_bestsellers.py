"""
Auto-generated Playwright script (Python)
Amazon – Best Sellers (Books)
Category: "Books"

Generated on: 2026-04-18T04:46:59.403Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BestsellersRequest:
    category: str = "Books"
    max_books: int = 5


@dataclass
class Book:
    rank: str = ""
    title: str = ""
    author: str = ""
    price: str = ""
    rating: str = ""


@dataclass
class BestsellersResult:
    books: list = field(default_factory=list)


def amazon_bestsellers(page: Page, request: BestsellersRequest) -> BestsellersResult:
    """Get Amazon Best Sellers in Books."""
    print(f"  Category: {request.category}\n")

    url = "https://www.amazon.com/best-sellers-books-Amazon/zgbs/books"
    print(f"Loading {url}...")
    checkpoint("Navigate to Amazon Best Sellers Books")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract bestseller books")
    books_data = page.evaluate(r"""(maxBooks) => {
        const results = [];
        const items = document.querySelectorAll(
            '[id^="gridItemRoot"], .zg-grid-general-faceout, .a-list-item'
        );
        let rank = 1;
        for (const item of items) {
            if (results.length >= maxBooks) break;
            const text = item.innerText || '';
            const lines = text.split('\n').map(l => l.trim()).filter(Boolean);

            let title = '', author = '', price = '', rating = '';

            // Find title - usually longest line that isn't price
            for (const line of lines) {
                if (line.length > 10 && line.length < 200 && !/^\$/.test(line) && !title) {
                    title = line;
                }
            }
            if (!title) continue;

            // Author
            for (const line of lines) {
                if (line !== title && line.length > 3 && line.length < 80 && !/^\$|^\d/.test(line) && !/stars?/i.test(line)) {
                    author = line;
                    break;
                }
            }

            // Price
            for (const line of lines) {
                const pm = line.match(/\$(\d+\.\d{2})/);
                if (pm) { price = pm[0]; break; }
            }

            // Rating
            for (const line of lines) {
                const rm = line.match(/(\d+\.\d)\s*out of/);
                if (rm) { rating = rm[1]; break; }
            }

            results.push({
                rank: String(rank),
                title,
                author,
                price,
                rating
            });
            rank++;
        }
        return results;
    }""", request.max_books)

    result = BestsellersResult(books=[Book(**b) for b in books_data])

    print("\n" + "=" * 60)
    print(f"Amazon Best Sellers: {request.category}")
    print("=" * 60)
    for b in result.books:
        print(f"  #{b.rank} {b.title}")
        print(f"      Author: {b.author}  Price: {b.price}  Rating: {b.rating}")
    print(f"\n  Total: {len(result.books)} books")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("amazon_bestsellers")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = amazon_bestsellers(page, BestsellersRequest())
            print(f"\nReturned {len(result.books)} books")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
