"""
Playwright script (Python) — eBay Seller Info Lookup
Search for a product, click the first result, and extract seller info.

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
from urllib.parse import quote
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class EbaySellerInfoRequest:
    query: str


@dataclass(frozen=True)
class EbaySellerInfoResult:
    query: str
    seller_name: str
    feedback_score: str
    positive_feedback_pct: str


# Searches eBay for a product query, clicks the first result, and extracts
# the seller name, feedback score, and positive feedback percentage.
def lookup_ebay_seller_info(
    page: Page,
    request: EbaySellerInfoRequest,
) -> EbaySellerInfoResult:
    query = request.query

    print(f"  Query: {query}\n")

    seller_name = "N/A"
    feedback_score = "N/A"
    positive_feedback_pct = "N/A"

    try:
        # ── Navigate to search results ────────────────────────────────────
        url = f"https://www.ebay.com/sch/i.html?_nkw={quote(query)}"
        print(f"Loading {url}...")
        checkpoint(f"Navigate to eBay search for {query}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)
        print(f"  URL: {page.url}")

        # ── STEP 1: Find and click first real result ──────────────────────
        print("STEP 1: Click first product result...")

        items = page.locator("ul.srp-results > li")
        count = items.count()
        print(f"  Found {count} result items")

        product_url = None
        for i in range(min(count, 15)):
            item = items.nth(i)
            link = item.locator("a[href*='/itm/']").first
            if link.count() == 0:
                continue
            href = link.evaluate("el => el.getAttribute('href')") or ""
            title_text = item.inner_text(timeout=2000)[:80].split("\n")[0]
            if "Shop on eBay" in title_text or "Find more like this" in title_text or not title_text:
                continue
            if "/itm/" in href:
                product_url = href
                print(f"  Selected: \"{title_text}\"")
                break

        if not product_url:
            print("  ERROR: No product found in search results")
            return EbaySellerInfoResult(
                query=query,
                seller_name=seller_name,
                feedback_score=feedback_score,
                positive_feedback_pct=positive_feedback_pct,
            )

        checkpoint(f"Navigate to product page")
        page.goto(product_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)
        print(f"  Product URL: {page.url}")

        # ── STEP 2: Extract seller info ───────────────────────────────────
        print("STEP 2: Extract seller info...")

        seller_card = page.locator('[data-testid="x-sellercard-atf"]')
        if seller_card.count() == 0:
            print("  Seller card not found, trying fallback...")
            seller_card = page.locator(".x-sellercard-atf")

        if seller_card.count() > 0:
            card_text = seller_card.first.inner_text(timeout=3000).strip()
            print(f"  Seller card text: \"{card_text[:100]}\"")

            # Seller name
            try:
                info_el = page.locator(".x-sellercard-atf__info").first
                info_text = info_el.inner_text(timeout=2000).strip()
                name_line = info_text.split("\n")[0].strip()
                seller_name = name_line
            except Exception:
                pass

            # Feedback score
            try:
                about = page.locator('[data-testid="x-sellercard-atf__about-seller"]').first
                about_text = about.inner_text(timeout=2000).strip()
                m = re.search(r"\((\d[\d,]*)\)", about_text)
                if m:
                    feedback_score = m.group(1)
            except Exception:
                pass

            # Positive feedback %
            try:
                data_items = page.locator('[data-testid="x-sellercard-atf__data-item"]')
                if data_items.count() > 0:
                    first_text = data_items.first.inner_text(timeout=2000).strip()
                    m = re.search(r"(\d+(?:\.\d+)?%)\s*positive", first_text)
                    if m:
                        positive_feedback_pct = m.group(1)
            except Exception:
                pass

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nSeller info for first result of '{query}':")
        print(f"  Seller Name:     {seller_name}")
        print(f"  Feedback Score:  {feedback_score}")
        print(f"  Positive %:      {positive_feedback_pct}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return EbaySellerInfoResult(
        query=query,
        seller_name=seller_name,
        feedback_score=feedback_score,
        positive_feedback_pct=positive_feedback_pct,
    )


def test_lookup_ebay_seller_info() -> None:
    request = EbaySellerInfoRequest(
        query="vintage watch",
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
            result = lookup_ebay_seller_info(page, request)
            assert result.query == request.query
            print(f"\n--- Summary ---")
            print(f"  Seller Name: {result.seller_name}")
            print(f"  Feedback Score: {result.feedback_score}")
            print(f"  Positive %: {result.positive_feedback_pct}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_lookup_ebay_seller_info)
