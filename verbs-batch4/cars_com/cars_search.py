import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class CarsSearchRequest:
    make: str = "Toyota"
    model: str = "Camry"
    zip_code: str = "60601"
    distance: int = 50
    max_results: int = 5

@dataclass(frozen=True)
class CarListing:
    title: str = ""
    price: str = ""
    mileage: str = ""
    dealer_name: str = ""
    location: str = ""

@dataclass(frozen=True)
class CarsSearchResult:
    listings: list = None  # list[CarListing]

# Search for used cars on Cars.com by make, model, and zip code,
# then extract listings with title, price, mileage, dealer name, and location.
def cars_search(page: Page, request: CarsSearchRequest) -> CarsSearchResult:
    make = request.make
    model = request.model
    zip_code = request.zip_code
    distance = request.distance
    max_results = request.max_results
    print(f"  Searching: {make} {model}, zip={zip_code}, {distance}mi, max={max_results}\n")

    url = (
        f"https://www.cars.com/shopping/results/"
        f"?stock_type=used"
        f"&makes[]={make.lower()}"
        f"&models[]={make.lower()}-{model.lower()}"
        f"&zip={zip_code}"
        f"&maximum_distance={distance}"
    )
    print(f"Loading {url}...")
    checkpoint(f"Navigate to {url}")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    print(f"  Loaded: {page.url}")

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""

    results = []

    # Try structured extraction via vehicle card elements
    cards = page.locator(
        'div.vehicle-card, '
        '[data-test="vehicleCardLink"], '
        'div[class*="vehicle-card"]'
    )
    count = cards.count()
    print(f"  Found {count} vehicle cards via selectors")

    if count > 0:
        for i in range(min(count, max_results)):
            card = cards.nth(i)
            try:
                card_text = card.inner_text(timeout=3000).strip()
                lines = [l.strip() for l in card_text.split("\n") if l.strip()]

                title = "N/A"
                price = "N/A"
                mileage = "N/A"
                dealer_name = "N/A"
                location = "N/A"

                for line in lines:
                    # Price
                    pm = re.search(r'\$[\d,]+', line)
                    if pm and price == "N/A":
                        price = pm.group(0)
                        continue
                    # Mileage
                    mm = re.search(r'([\d,]+)\s*mi\.?', line, re.I)
                    if mm and mileage == "N/A":
                        mileage = mm.group(0)
                        continue
                    # Location (City, ST pattern)
                    lm = re.search(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}', line)
                    if lm and location == "N/A":
                        location = lm.group(0)
                        continue
                    # Title (year + make pattern)
                    tm = re.search(r'(20\d{2}|19\d{2})\s+\w+', line)
                    if tm and title == "N/A" and len(line) > 8:
                        title = line
                        continue
                    # Dealer name (not matched above, reasonable length)
                    if (len(line) > 5 and dealer_name == "N/A"
                            and not re.match(r'^[\$\d]', line)
                            and title != "N/A" and price != "N/A"):
                        dealer_name = line

                if title != "N/A":
                    results.append(CarListing(
                        title=title,
                        price=price,
                        mileage=mileage,
                        dealer_name=dealer_name,
                        location=location,
                    ))
            except Exception:
                continue

    # Fallback: text-based extraction using year pattern anchors
    if not results:
        print("  Card selectors missed, trying text-based extraction...")
        text_lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        i = 0
        while i < len(text_lines) and len(results) < max_results:
            line = text_lines[i]
            tm = re.search(r'(20\d{2}|19\d{2})\s+\w+', line)
            if tm and len(line) > 10:
                title = line
                price = "N/A"
                mileage = "N/A"
                dealer_name = "N/A"
                location = "N/A"

                for j in range(i + 1, min(len(text_lines), i + 10)):
                    nearby = text_lines[j]
                    pm = re.search(r'\$[\d,]+', nearby)
                    if pm and price == "N/A":
                        price = pm.group(0)
                    mmatch = re.search(r'([\d,]+)\s*mi\.?', nearby, re.I)
                    if mmatch and mileage == "N/A":
                        mileage = mmatch.group(0)
                    lm = re.search(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}', nearby)
                    if lm and location == "N/A":
                        location = lm.group(0)
                    if (len(nearby) > 5 and dealer_name == "N/A"
                            and not re.match(r'^[\$\d]', nearby)
                            and not re.search(r'\d{4}\s+\w+', nearby)
                            and not re.search(r'mi\.?', nearby, re.I)):
                        dealer_name = nearby

                if price != "N/A" or mileage != "N/A":
                    results.append(CarListing(
                        title=title,
                        price=price,
                        mileage=mileage,
                        dealer_name=dealer_name,
                        location=location,
                    ))
            i += 1

    print("=" * 60)
    print(f"Cars.com – Used {make} {model} near {zip_code}")
    print("=" * 60)
    for idx, c in enumerate(results, 1):
        print(f"\n{idx}. {c.title}")
        print(f"   Price: {c.price}")
        print(f"   Mileage: {c.mileage}")
        print(f"   Dealer: {c.dealer_name}")
        print(f"   Location: {c.location}")

    print(f"\nFound {len(results)} listings")

    return CarsSearchResult(listings=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = cars_search(page, CarsSearchRequest())
        print(f"\nReturned {len(result.listings or [])} listings")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
