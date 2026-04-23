"""
Playwright script (Python) — Amazon.com Product Reviews
Search for a product, click the first result, extract customer reviews
with star rating, title, and review text.

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
class AmazonReviewsRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class AmazonReview:
    star_rating: str
    title: str
    review_text: str


@dataclass(frozen=True)
class AmazonReviewsResult:
    query: str
    product_name: str
    reviews: list[AmazonReview]


# Searches Amazon for a product query, clicks the first result, scrolls to the
# reviews section, and extracts up to max_results reviews with star rating, title,
# and review text.
def search_amazon_reviews(
    page: Page,
    request: AmazonReviewsRequest,
) -> AmazonReviewsResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}")
    print(f"  Max reviews: {max_results}\n")

    results: list[AmazonReview] = []
    product_name = "N/A"

    try:
        # ── Navigate ──────────────────────────────────────────────────────
        print("Loading Amazon.com...")
        checkpoint("Navigate to https://www.amazon.com")
        page.goto("https://www.amazon.com")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # ── Dismiss popups ────────────────────────────────────────────────
        for selector in [
            "#sp-cc-accept",
            "input[data-action-type='DISMISS']",
            "button:has-text('Accept')",
        ]:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {selector}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        # ── STEP 1: Search ────────────────────────────────────────────────
        print(f'STEP 1: Search for "{query}"...')
        search_input = page.locator('#twotabsearchtextbox').first
        checkpoint("Click search input")
        search_input.evaluate("el => el.click()")
        page.wait_for_timeout(500)
        page.keyboard.press("Control+a")
        checkpoint(f"Type query: {query}")
        search_input.type(query, delay=50)
        page.wait_for_timeout(1000)
        checkpoint("Press Enter to search")
        page.keyboard.press("Enter")
        print(f'  Typed "{query}" and pressed Enter')
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(4000)

        # ── STEP 2: Click first result ────────────────────────────────────
        print("STEP 2: Click the first search result...")
        first_result = page.locator(
            "[data-component-type='s-search-result'] [data-cy='title-recipe'] a[href^='/']"
        ).first
        first_result.wait_for(state="visible", timeout=10000)
        product_name = first_result.inner_text(timeout=5000).strip()
        href = first_result.get_attribute("href")
        product_url = f"https://www.amazon.com{href}"
        checkpoint(f"Navigate to product: {product_name}")
        page.goto(product_url)
        print(f'  Navigated to: "{product_name}"')
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(4000)

        # ── STEP 3: Scroll to reviews on product page ─────────────────
        print("STEP 3: Scroll to customer reviews section...")
        checkpoint("Scroll to reviews section")
        page.evaluate("""() => {
            const el = document.getElementById('reviewsMedley')
                    || document.getElementById('customer_review_section')
                    || document.querySelector('[data-hook="review"]');
            if (el) el.scrollIntoView({behavior: 'smooth'});
            else window.scrollBy(0, 3000);
        }""")
        page.wait_for_timeout(2000)

        # ── STEP 4: Extract reviews ───────────────────────────────────────
        print(f"STEP 4: Extract up to {max_results} reviews...")

        review_cards = page.locator('[data-hook="review"]')
        count = review_cards.count()
        print(f"  Found {count} review cards")

        for i in range(count):
            if len(results) >= max_results:
                break
            card = review_cards.nth(i)
            try:
                star_rating = "N/A"
                title = "N/A"
                review_text = "N/A"

                # Star rating
                try:
                    star_el = card.locator(
                        '[data-hook="review-star-rating"] .a-icon-alt, '
                        '[data-hook="cmps-review-star-rating"] .a-icon-alt'
                    ).first
                    star_text = star_el.inner_text(timeout=2000).strip()
                    sm = re.search(r"([\d.]+) out of", star_text)
                    if sm:
                        star_rating = sm.group(1)
                except Exception:
                    pass

                # Review title
                try:
                    title_el = card.locator(
                        '[data-hook="review-title"] span, '
                        '[data-hook="review-title"]'
                    ).first
                    title = title_el.inner_text(timeout=2000).strip()
                    title = re.sub(r'^\d+\.\d+ out of \d+ stars\s*', '', title).strip()
                except Exception:
                    pass

                # Review text
                try:
                    text_el = card.locator('[data-hook="review-body"] span').first
                    review_text = text_el.inner_text(timeout=2000).strip()
                    if len(review_text) > 300:
                        review_text = review_text[:300] + "..."
                except Exception:
                    pass

                if title == "N/A" and review_text == "N/A":
                    continue

                results.append(AmazonReview(
                    star_rating=star_rating,
                    title=title,
                    review_text=review_text,
                ))
                print(f"  {len(results)}. [{star_rating} stars] {title}")

            except Exception as e:
                print(f"  Error on review {i}: {e}")
                continue

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nFound {len(results)} reviews for '{query}' — Product: {product_name}")
        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r.star_rating} stars] {r.title}")
            print(f"     {r.review_text[:120]}...")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return AmazonReviewsResult(
        query=query,
        product_name=product_name,
        reviews=results,
    )


def test_search_amazon_reviews() -> None:
    request = AmazonReviewsRequest(
        query="wireless earbuds",
        max_results=5,
    )

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
            result = search_amazon_reviews(page, request)
            assert result.query == request.query
            assert len(result.reviews) <= request.max_results
            print(f"\nTotal reviews found: {len(result.reviews)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_amazon_reviews)
