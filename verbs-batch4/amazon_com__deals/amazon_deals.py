import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class AmazonDealsRequest:
    max_results: int = 5

@dataclass(frozen=True)
class AmazonDeal:
    product_name: str = ""
    deal_price: str = ""
    original_price: str = ""
    discount_percent: str = ""
    deal_type: str = ""

@dataclass(frozen=True)
class AmazonDealsResult:
    deals: list = None  # list[AmazonDeal]

# Navigate to Amazon's Today's Deals page and extract deal listings including
# product name, deal price, original price, discount percentage, and deal type.
def amazon_deals(page: Page, request: AmazonDealsRequest) -> AmazonDealsResult:
    max_results = request.max_results
    print(f"  Max deals to extract: {max_results}\n")

    url = "https://www.amazon.com/deals"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to {url}")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    print(f"  Loaded: {page.url}")

    # Check for bot detection
    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    if "Enter the characters you see below" in body_text or "CAPTCHA" in body_text:
        print("  WARNING: Bot detection / CAPTCHA triggered by Amazon.")
        return AmazonDealsResult(deals=[])

    results = []

    # Try structured extraction via deal card elements
    # Amazon uses data-testid attributes and specific grid layouts for deals
    cards = page.locator(
        '[data-testid="deal-card"], '
        '[class*="DealCard"], '
        '[data-component-type="s-search-result"], '
        'div[data-deal-id]'
    )
    count = cards.count()
    print(f"  Found {count} deal cards via selectors")

    if count > 0:
        for i in range(min(count, max_results)):
            card = cards.nth(i)
            try:
                card_text = card.inner_text(timeout=3000).strip()
                lines = [l.strip() for l in card_text.split("\n") if l.strip()]

                product_name = "N/A"
                deal_price = "N/A"
                original_price = "N/A"
                discount_percent = "N/A"
                deal_type = "N/A"

                for line in lines:
                    # Discount percentage
                    dm = re.search(r'(\d+)%\s*off', line, re.I)
                    if dm:
                        discount_percent = f"{dm.group(1)}% off"
                        continue
                    # Price
                    pm = re.search(r'\$[\d,.]+', line)
                    if pm:
                        if deal_price == "N/A":
                            deal_price = pm.group(0)
                        elif original_price == "N/A":
                            original_price = pm.group(0)
                        continue
                    # Deal type keywords
                    if any(kw in line.lower() for kw in [
                        'lightning', 'deal of the day', 'best deal',
                        'limited time', 'top deal', 'prime'
                    ]):
                        deal_type = line
                        continue
                    # Product name (longest line > 10 chars, not a price line)
                    if len(line) > 10 and not re.match(r'^[\$\d%]', line):
                        if product_name == "N/A" or len(line) > len(product_name):
                            product_name = line

                if product_name != "N/A":
                    results.append(AmazonDeal(
                        product_name=product_name,
                        deal_price=deal_price,
                        original_price=original_price,
                        discount_percent=discount_percent,
                        deal_type=deal_type,
                    ))
            except Exception:
                continue

    # Fallback: text-based extraction using discount pattern anchors
    if not results:
        print("  Card selectors missed, trying text-based extraction...")
        text_lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        i = 0
        while i < len(text_lines) and len(results) < max_results:
            line = text_lines[i]
            dm = re.search(r'(\d+)%\s*off', line, re.I)
            if dm:
                discount_percent = f"{dm.group(1)}% off"
                deal_price = "N/A"
                original_price = "N/A"
                product_name = "N/A"
                deal_type = "N/A"

                # Search nearby lines (within 5 lines) for price/name
                for j in range(max(0, i - 3), min(len(text_lines), i + 5)):
                    nearby = text_lines[j]
                    pm = re.search(r'\$[\d,.]+', nearby)
                    if pm:
                        if deal_price == "N/A":
                            deal_price = pm.group(0)
                        elif original_price == "N/A":
                            original_price = pm.group(0)
                    if any(kw in nearby.lower() for kw in [
                        'lightning', 'deal of the day', 'best deal',
                        'limited time', 'top deal', 'prime'
                    ]):
                        deal_type = nearby
                    if (len(nearby) > 20
                            and not re.match(r'^[\$\d%]', nearby)
                            and nearby != line
                            and len(nearby) > len(product_name)):
                        product_name = nearby

                if product_name != "N/A" or deal_price != "N/A":
                    results.append(AmazonDeal(
                        product_name=product_name,
                        deal_price=deal_price,
                        original_price=original_price,
                        discount_percent=discount_percent,
                        deal_type=deal_type,
                    ))
            i += 1

    print("=" * 60)
    print("Amazon - Today's Deals")
    print("=" * 60)
    for idx, d in enumerate(results, 1):
        print(f"\n{idx}. {d.product_name}")
        print(f"   Price: {d.deal_price}  (was {d.original_price})")
        print(f"   Discount: {d.discount_percent}")
        print(f"   Type: {d.deal_type}")

    print(f"\nFound {len(results)} deals")

    return AmazonDealsResult(deals=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = amazon_deals(page, AmazonDealsRequest())
        print(f"\nReturned {len(result.deals or [])} deals")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
