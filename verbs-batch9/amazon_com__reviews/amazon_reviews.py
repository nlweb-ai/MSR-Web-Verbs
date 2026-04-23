"""
Playwright script (Python) — Amazon Product Reviews Extraction
Search for a product and extract customer reviews.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class AmazonReviewsRequest:
    search_query: str = "kindle paperwhite"
    max_results: int = 5


@dataclass
class ReviewItem:
    reviewer_name: str = ""
    star_rating: str = ""
    review_title: str = ""
    review_date: str = ""
    review_text: str = ""


@dataclass
class AmazonReviewsResult:
    product_name: str = ""
    items: List[ReviewItem] = field(default_factory=list)


# Searches Amazon for a product, navigates to the reviews page, and extracts reviews.
def get_amazon_reviews(page: Page, request: AmazonReviewsRequest) -> AmazonReviewsResult:
    """Get Amazon product reviews."""
    encoded = quote_plus(request.search_query)
    url = f"https://www.amazon.com/s?k={encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Amazon search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Click first product
    checkpoint("Click first product")
    try:
        first_product = page.locator('[data-component-type="s-search-result"] h2 a').first
        product_name = first_product.text_content(timeout=10000).strip()
    except Exception:
        # Fallback selectors
        first_product = page.locator('.s-result-item h2 a, .s-card-container h2 a, [data-cy="title-recipe"] a').first
        product_name = first_product.text_content(timeout=10000).strip()
    print(f"Opening: {product_name}")
    first_product.click()
    page.wait_for_timeout(5000)

    # Scroll to reviews
    checkpoint("Scroll to reviews")
    page.evaluate("document.getElementById('customerReviews')?.scrollIntoView()")
    page.wait_for_timeout(2000)

    result = AmazonReviewsResult(product_name=product_name)

    checkpoint("Extract reviews")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();
        const reviews = document.querySelectorAll('[data-hook="review"], [id^="customer_review"]');
        let candidates = Array.from(reviews);
        candidates = candidates.filter(c => !candidates.some(o => o !== c && o.contains(c)));
        for (const rev of candidates) {
            if (items.length >= max) break;

            let reviewer = '';
            const nameEl = rev.querySelector('[data-hook="review-author"] span, .a-profile-name');
            if (nameEl) reviewer = nameEl.textContent.trim();

            let stars = '';
            const starEl = rev.querySelector('[data-hook="review-star-rating"], [data-hook="cmps-review-star-rating"]');
            if (starEl) {
                const sm = starEl.textContent.match(/(\\d\\.?\\d?)\\s*out/);
                if (sm) stars = sm[1];
            }

            let title = '';
            const titleEl = rev.querySelector('[data-hook="review-title"]');
            if (titleEl) {
                const lines = titleEl.innerText.split('\\n').map(l => l.trim()).filter(l => l && !l.match(/out of \\d/));
                title = lines[lines.length - 1] || '';
            }

            let date = '';
            const dateEl = rev.querySelector('[data-hook="review-date"]');
            if (dateEl) date = dateEl.textContent.trim();

            let text = '';
            const textEl = rev.querySelector('[data-hook="review-body"] span, .review-text');
            if (textEl) text = textEl.textContent.trim().substring(0, 200);

            const key = reviewer + '|' + title;
            if ((reviewer || title) && !seen.has(key)) {
                seen.add(key);
                items.push({reviewer_name: reviewer, star_rating: stars, review_title: title, review_date: date, review_text: text});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ReviewItem()
        item.reviewer_name = d.get("reviewer_name", "")
        item.star_rating = d.get("star_rating", "")
        item.review_title = d.get("review_title", "")
        item.review_date = d.get("review_date", "")
        item.review_text = d.get("review_text", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} reviews for '{product_name}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. [{item.star_rating}★] {item.review_title}")
        print(f"     By: {item.reviewer_name} — {item.review_date}")
        print(f"     {item.review_text[:100]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("amazon_reviews")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = get_amazon_reviews(page, AmazonReviewsRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} reviews")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
