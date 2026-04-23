"""
Yellow Pages – Business Search verb
Search Yellow Pages for businesses by type and location, extract listings.
"""

import re
import os
from dataclasses import dataclass
from urllib.parse import quote as url_quote
from playwright.sync_api import Page, sync_playwright

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

# ── Types ─────────────────────────────────────────────────────────────────────

@dataclass
class YellowPagesSearchRequest:
    search_term: str    # e.g. "plumber"
    location: str       # e.g. "Chicago, IL"
    max_results: int    # number of listings to extract

@dataclass
class YellowPagesListing:
    business_name: str  # name of the business
    phone_number: str   # e.g. "(312) 555-1234"
    address: str        # street address
    rating: str         # e.g. "4.5" or "N/A"

@dataclass
class YellowPagesSearchResult:
    listings: list  # list of YellowPagesListing

# ── Verb ──────────────────────────────────────────────────────────────────────

def yellowpages_search(page: Page, request: YellowPagesSearchRequest) -> YellowPagesSearchResult:
    """
    Search Yellow Pages for businesses and extract listings.

    Args:
        page: Playwright page.
        request: YellowPagesSearchRequest with search_term, location, and max_results.

    Returns:
        YellowPagesSearchResult containing a list of YellowPagesListing.
    """
    search_url = (
        f"https://www.yellowpages.com/search?"
        f"search_terms={url_quote(request.search_term)}"
        f"&geo_location_terms={url_quote(request.location)}"
    )
    print(f"Loading {search_url}...")
    page.goto(search_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(4000)
    print(f"  Loaded: {page.url}")
    checkpoint("Loaded Yellow Pages results")

    # Dismiss cookie / consent dialogs
    for selector in [
        'button:has-text("Accept")',
        'button:has-text("Accept All")',
        'button:has-text("Got it")',
        '#onetrust-accept-btn-handler',
    ]:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=1500):
                btn.click()
                page.wait_for_timeout(500)
                break
        except Exception:
            pass

    # Extract business listings
    print(f"Extracting up to {request.max_results} listings...")

    # Try multiple selector strategies
    listing_cards = page.locator(
        'div.result, '
        'div.v-card, '
        'div.search-results div.info, '
        '[class*="srp-listing"]'
    )
    count = listing_cards.count()
    print(f"  Found {count} listing cards (primary)")

    if count == 0:
        # Broader fallback
        listing_cards = page.locator('[class*="organic"] [class*="info"], .organic .info-section')
        count = listing_cards.count()
        print(f"  Fallback: found {count} cards")

    results = []
    seen_names = set()
    for i in range(count):
        if len(results) >= request.max_results:
            break
        card = listing_cards.nth(i)
        try:
            # Skip ad/sponsored results
            try:
                card_class = card.get_attribute("class", timeout=500) or ""
                if "ad" in card_class.lower() or "sponsored" in card_class.lower():
                    continue
            except Exception:
                pass

            # Business name
            biz_name = "N/A"
            try:
                name_el = card.locator(
                    'a.business-name, '
                    'h2 a, '
                    '[class*="business-name"], '
                    'a[class*="name"]'
                ).first
                biz_name = name_el.inner_text(timeout=2000).strip()
            except Exception:
                pass

            if biz_name == "N/A" or biz_name.lower() in seen_names:
                continue
            seen_names.add(biz_name.lower())

            # Phone number
            phone = "N/A"
            try:
                phone_el = card.locator(
                    '[class*="phone"], '
                    'a[href^="tel:"], '
                    '[data-phone]'
                ).first
                phone = phone_el.inner_text(timeout=2000).strip()
            except Exception:
                pass

            # Address
            address = "N/A"
            try:
                addr_el = card.locator(
                    '[class*="adr"], '
                    '[class*="address"], '
                    '[class*="street-address"], '
                    '.locality'
                ).first
                address = addr_el.inner_text(timeout=2000).strip()
                address = re.sub(r"\s+", " ", address).strip()
            except Exception:
                pass

            # Rating
            rating = "N/A"
            try:
                rating_el = card.locator(
                    'div.result-rating, '
                    '[class*="result-rating"]'
                ).first
                rating_class = rating_el.get_attribute("class", timeout=2000) or ""
                rating_words = {
                    "one": 1, "two": 2, "three": 3,
                    "four": 4, "five": 5,
                }
                base = 0
                for word, val in rating_words.items():
                    if word in rating_class:
                        base = val
                        break
                if base > 0:
                    if "half" in rating_class:
                        rating = str(base + 0.5)
                    else:
                        rating = str(base)
            except Exception:
                pass
            if rating == "N/A":
                try:
                    review_el = card.locator('a.rating span, [class*="rating"] span').first
                    review_text = review_el.inner_text(timeout=1000).strip()
                    rm = re.search(r"([\d.]+)", review_text)
                    if rm:
                        rating = rm.group(1)
                except Exception:
                    pass

            results.append(YellowPagesListing(
                business_name=biz_name,
                phone_number=phone,
                address=address,
                rating=rating,
            ))
        except Exception:
            continue

    # Fallback: regex on page text
    if not results:
        print("  Card extraction failed, trying text fallback...")
        body_text = page.evaluate("document.body.innerText") or ""
        lines = body_text.split("\n")
        for i, line in enumerate(lines):
            if len(results) >= request.max_results:
                break
            phone_match = re.search(r"\(\d{3}\)\s*\d{3}-\d{4}", line)
            if phone_match:
                biz_name = "N/A"
                for j in range(max(0, i - 3), i):
                    cand = lines[j].strip()
                    if cand and len(cand) > 3 and not re.match(r"^\(", cand):
                        biz_name = cand
                if biz_name != "N/A":
                    results.append(YellowPagesListing(
                        business_name=biz_name,
                        phone_number=phone_match.group(0),
                        address="N/A",
                        rating="N/A",
                    ))

    checkpoint("Extracted business listings")
    print(f'\nFound {len(results)} listings for "{request.search_term}" in "{request.location}":')
    for i, biz in enumerate(results, 1):
        print(f"  {i}. {biz.business_name}")
        print(f"     Phone: {biz.phone_number}  Address: {biz.address}  Rating: {biz.rating}")

    return YellowPagesSearchResult(listings=results)

# ── Test ──────────────────────────────────────────────────────────────────────

def test_func():

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()

        request = YellowPagesSearchRequest(search_term="plumber", location="Chicago, IL", max_results=5)
        result = yellowpages_search(page, request)
        print(f"\nTotal listings found: {len(result.listings)}")

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
