"""
Auto-generated Playwright script (Python)
Amazon – Coupons Page

Uses CDP-launched Chrome to avoid bot detection.
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CouponRequest:
    max_results: int = 5


@dataclass
class CouponResult:
    product_name: str = ""
    discount: str = ""
    price: str = ""
    category: str = ""


def amazon_coupons(page: Page, request: CouponRequest) -> list:
    """Extract coupon deals from Amazon coupons page."""
    print(f"  Max results: {request.max_results}\n")

    # ── Navigate to Amazon coupons ────────────────────────────────────
    url = "https://www.amazon.com/coupons"
    print(f"Loading {url}...")
    checkpoint("Navigate to Amazon coupons")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    # ── Extract coupon cards ──────────────────────────────────────────
    checkpoint("Extract coupon deals")
    results = []

    # Use JS extraction for reliability (virtualized grid)
    data = page.evaluate("""() => {
        const cards = document.querySelectorAll('[data-testid="product-card"]');
        return Array.from(cards).map(card => {
            // Discount: look for text pattern "Save X%" or "Save $X"
            const allSpans = card.querySelectorAll('span');
            let discount = '';
            for (const s of allSpans) {
                const t = s.textContent.trim();
                if (t.startsWith('Save ') && t.length < 30) { discount = t; break; }
            }
            const nameEl = card.querySelector('span.a-truncate-full.a-offscreen');
            const priceEl = card.querySelector('span.a-price span.a-offscreen');
            const imgEl = card.querySelector('img');
            return {
                discount: discount,
                name: nameEl ? nameEl.textContent.trim() : (imgEl ? imgEl.alt : ''),
                price: priceEl ? priceEl.textContent.trim().replace('Price: ', '') : '',
            };
        });
    }""")

    for item in data[:request.max_results]:
        coupon = CouponResult(
            product_name=item.get("name", ""),
            discount=item.get("discount", ""),
            price=item.get("price", ""),
            category="Coupons",
        )
        if coupon.product_name or coupon.discount:
            results.append(coupon)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("Amazon Coupon Deals")
    print("=" * 70)
    for i, c in enumerate(results, 1):
        print(f"  {i}. {c.product_name[:60]}")
        print(f"     Discount: {c.discount}")
        print(f"     Price:    {c.price}")
        print(f"     Category: {c.category}")
        print()

    return results


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("amazon_coupons")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            results = amazon_coupons(page, CouponRequest())
            print(f"\nDone. Found {len(results)} coupons.")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
