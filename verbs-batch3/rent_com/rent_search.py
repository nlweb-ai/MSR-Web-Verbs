import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


PRICE_RE = re.compile(r'^\$[\d,]+\+?$')


@dataclass(frozen=True)
class RentSearchRequest:
    url: str = "https://www.rent.com/illinois/chicago-apartments/2-bedrooms"
    max_results: int = 5


@dataclass(frozen=True)
class ApartmentListing:
    name: str = ""
    price: str = ""
    bedrooms: str = ""
    neighborhood: str = ""


@dataclass(frozen=True)
class RentSearchResult:
    listings: list = None  # list[ApartmentListing]


# Search for apartments on Rent.com and extract listing details including
# property name, price range, bedrooms, and neighborhood from the results page.
def rent_search(page: Page, request: RentSearchRequest) -> RentSearchResult:
    url = request.url
    max_results = request.max_results
    results = []

    print(f"  URL: {url}\n")

    checkpoint("Navigate to Rent.com search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Skip to search results ('Rentals Available')
    i = 0
    while i < len(text_lines):
        if 'Rentals Available' in text_lines[i]:
            i += 1
            break
        i += 1

    # Skip 'Sort by:' and 'Best Match'
    while i < len(text_lines) and text_lines[i] in ('Sort by:', 'Best Match'):
        i += 1

    while i < len(text_lines) and len(results) < max_results:
        line = text_lines[i]

        # 'Save' marker appears right after price in each listing
        if line == 'Save' and i > 0 and i + 5 < len(text_lines):
            price = text_lines[i - 1]
            if PRICE_RE.match(price) or price == 'Contact for Price':
                beds = text_lines[i + 1]
                bath = text_lines[i + 2]
                sqft = text_lines[i + 3]
                address = text_lines[i + 4]
                name = text_lines[i + 5]

                # Extract neighborhood from address
                neighborhood = address.split(', ')[1] if ', ' in address else 'N/A'

                results.append(ApartmentListing(
                    name=name,
                    price=price,
                    bedrooms=beds,
                    neighborhood=address,
                ))

        i += 1

    print("=" * 60)
    print("Apartments (search results)")
    print("=" * 60)
    for idx, r in enumerate(results, 1):
        print(f"\n{idx}. {r.name}")
        print(f"   Price:    {r.price}")
        print(f"   Beds:     {r.bedrooms}")
        print(f"   Address:  {r.neighborhood}")

    print(f"\nFound {len(results)} listings")

    return RentSearchResult(listings=results)


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_user_data = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            chrome_user_data,
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        request = RentSearchRequest()
        result = rent_search(page, request)
        print(f"\nReturned {len(result.listings)} listings")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)