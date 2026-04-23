"""
Auto-generated Playwright script (Python)
Edmunds – Car Review
Car: "2024 Honda Civic"

Generated on: 2026-04-18T05:12:42.306Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CarRequest:
    car: str = "2024 Honda Civic"


@dataclass
class CarResult:
    model: str = ""
    rating: str = ""
    msrp: str = ""
    mpg: str = ""
    pros: str = ""
    cons: str = ""


def edmunds_search(page: Page, request: CarRequest) -> CarResult:
    """Search Edmunds for car reviews.
    
    NOTE: Edmunds.com has heavy bot detection (403 Access Denied).
    This script attempts to access the review page but may be blocked.
    """
    print(f"  Car: {request.car}\n")

    # ── Step 1: Try direct Edmunds review URL ─────────────────────────
    # Parse "2024 Honda Civic" → /honda/civic/2024/review/
    parts = request.car.lower().split()
    year = ""
    make = ""
    model = ""
    for p in parts:
        if p.isdigit() and len(p) == 4:
            year = p
        elif not make:
            make = p
        else:
            model = p

    url = f"https://www.edmunds.com/{make}/{model}/{year}/review/"
    print(f"Loading {url}...")
    checkpoint("Navigate to Edmunds review page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Check for bot block
    title = page.title()
    if "403" in title or "Access Denied" in title:
        print("  Edmunds blocked access (403 - bot detection).")
        print("  This site has heavy anti-bot protection.")
        return CarResult(model=request.car)

    # ── Step 2: Extract review data ───────────────────────────────────
    checkpoint("Extract car review data")
    data = page.evaluate(r"""() => {
        const text = document.body.innerText;
        const result = {};

        // Model name
        const h1 = document.querySelector('h1');
        result.model = h1 ? h1.innerText.trim() : '';

        // Rating
        const ratingEl = document.querySelector('[data-testid="rating"], [class*="rating"]');
        result.rating = ratingEl ? ratingEl.innerText.trim() : '';

        // MSRP
        const msrpMatch = text.match(/MSRP[:\s]*\$[\d,]+\s*[-–]\s*\$[\d,]+/i) || text.match(/\$[\d,]+\s*[-–]\s*\$[\d,]+/);
        result.msrp = msrpMatch ? msrpMatch[0] : '';

        // MPG
        const mpgMatch = text.match(/(\d+)\s*(?:city|cty)\s*\/?\s*(\d+)\s*(?:hwy|highway)/i);
        result.mpg = mpgMatch ? `${mpgMatch[1]} city / ${mpgMatch[2]} highway` : '';

        return result;
    }""")

    result = CarResult(
        model=data.get("model", request.car),
        rating=data.get("rating", ""),
        msrp=data.get("msrp", ""),
        mpg=data.get("mpg", ""),
    )

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Edmunds: {result.model}")
    print("=" * 60)
    print(f"  Rating: {result.rating}")
    print(f"  MSRP:   {result.msrp}")
    print(f"  MPG:    {result.mpg}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("edmunds_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = edmunds_search(page, CarRequest())
            print(f"\nReturned info for {result.model}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
