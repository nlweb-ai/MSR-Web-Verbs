import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class GoodRxSearchRequest:
    drug: str = "metformin"
    max_results: int = 5

@dataclass(frozen=True)
class PharmacyPrice:
    pharmacy_name: str = ""
    price: str = ""

@dataclass(frozen=True)
class GoodRxSearchResult:
    drug_name: str = ""
    dosage: str = ""
    prices: list = None  # list[PharmacyPrice]

# Search for a prescription drug on GoodRx and extract pharmacy prices.
def goodrx_search(page: Page, request: GoodRxSearchRequest) -> GoodRxSearchResult:
    drug = request.drug
    max_results = request.max_results
    print(f"  Drug: {drug}")
    print(f"  Max results: {max_results}\n")

    url = f"https://www.goodrx.com/{drug.lower().replace(' ', '-')}"
    print(f"Loading {url}...")
    checkpoint("Navigate to GoodRx")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""

    drug_name = "N/A"
    dosage = "N/A"
    prices = []

    # Try to extract drug name from heading elements
    headings = page.locator("h1")
    if headings.count() > 0:
        h1_text = headings.first.inner_text(timeout=3000).strip()
        if h1_text:
            drug_name = h1_text

    # Try to extract dosage from page
    dosage_match = re.search(
        r'(\d+\s*mg(?:\s*/\s*\d+\s*mg)?(?:\s+tablet(?:s)?)?)',
        body_text, re.IGNORECASE
    )
    if dosage_match:
        dosage = dosage_match.group(1).strip()

    # Try structured extraction via pharmacy price cards
    price_cards = page.locator(
        '[class*="PharmacyCard"], '
        '[class*="pharmacy-card"], '
        '[class*="PriceRow"], '
        '[class*="price-row"], '
        '[data-testid*="pharmacy"], '
        '[class*="Pharmacy"]'
    )
    count = price_cards.count()
    print(f"  Found {count} pharmacy cards via selectors")

    if count > 0:
        for i in range(min(count, max_results)):
            card = price_cards.nth(i)
            try:
                card_text = card.inner_text(timeout=3000).strip()
                lines = [l.strip() for l in card_text.split("\n") if l.strip()]

                pharmacy_name = "N/A"
                price = "N/A"

                for line in lines:
                    # Price pattern: $XX.XX
                    pm = re.search(r'\$\s?([\d,]+(?:\.\d{2})?)', line)
                    if pm and price == "N/A":
                        price = "$" + pm.group(1)
                        continue
                    # Pharmacy name — longer descriptive text, not a price
                    if (len(line) > 2 and not re.match(r'^[\$\d,.\s]+$', line)
                            and pharmacy_name == "N/A"):
                        pharmacy_name = line

                if pharmacy_name != "N/A" or price != "N/A":
                    prices.append(PharmacyPrice(
                        pharmacy_name=pharmacy_name,
                        price=price,
                    ))
            except Exception:
                continue

    # Fallback: text-based extraction
    if not prices:
        print("  Card selectors missed, trying text-based extraction...")
        text_lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        known_pharmacies = [
            "CVS", "Walgreens", "Walmart", "Rite Aid", "Kroger",
            "Costco", "Sam's Club", "Target", "Safeway", "Albertsons",
            "Publix", "H-E-B", "Meijer", "Hy-Vee", "Winn-Dixie",
            "Amazon Pharmacy", "Capsule", "Alto Pharmacy",
        ]

        i = 0
        while i < len(text_lines) and len(prices) < max_results:
            line = text_lines[i]
            matched_pharmacy = None

            # Check if line contains a known pharmacy name
            for pname in known_pharmacies:
                if pname.lower() in line.lower():
                    matched_pharmacy = pname
                    break

            if matched_pharmacy:
                price = "N/A"
                # Look in nearby lines for a price
                for j in range(max(0, i - 2), min(len(text_lines), i + 5)):
                    pm = re.search(r'\$\s?([\d,]+(?:\.\d{2})?)', text_lines[j])
                    if pm:
                        price = "$" + pm.group(1)
                        break

                prices.append(PharmacyPrice(
                    pharmacy_name=matched_pharmacy,
                    price=price,
                ))
                i += 3
                continue
            i += 1

        prices = prices[:max_results]

    # If drug_name still N/A, try from body text
    if drug_name == "N/A":
        dm = re.search(
            rf'({re.escape(drug)}(?:\s+\w+)*)',
            body_text, re.IGNORECASE
        )
        if dm:
            drug_name = dm.group(1).strip()

    print("=" * 60)
    print(f"GoodRx - Prices for \"{drug_name}\"")
    print(f"  Dosage: {dosage}")
    print("=" * 60)
    for idx, p in enumerate(prices, 1):
        print(f"\n{idx}. {p.pharmacy_name}")
        print(f"   Price: {p.price}")

    print(f"\nFound {len(prices)} pharmacy prices")

    return GoodRxSearchResult(
        drug_name=drug_name,
        dosage=dosage,
        prices=prices,
    )

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = goodrx_search(page, GoodRxSearchRequest())
        print(f"\nReturned {len(result.prices or [])} pharmacy prices")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
