import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


PRICE_RE = re.compile(r'^(?:From)?\$([\d,]+)')
BED_RE = re.compile(r'^(\d+)bed$')
BATH_RE = re.compile(r'^([\d.]+)bath$')
SQFT_RE = re.compile(r'^([\d,]+)sqft$')


@dataclass(frozen=True)
class RealtorSearchRequest:
    location: str = "Austin_TX"
    price_min: int = 300000
    price_max: int = 500000
    max_results: int = 5


@dataclass(frozen=True)
class HomeListing:
    address: str = "N/A"
    price: str = "N/A"
    bedrooms: str = "N/A"
    bathrooms: str = "N/A"
    sqft: str = "N/A"


@dataclass(frozen=True)
class RealtorSearchResult:
    listings: list  # list[HomeListing]
    total_found: int = 0


# Search for homes for sale on realtor.com filtered by location and price range,
# then extract listing details (address, price, bedrooms, bathrooms, sqft).
def realtor_search(page: Page, request: RealtorSearchRequest) -> RealtorSearchResult:
    print(f"  Location: {request.location}, Price: ${request.price_min:,}-${request.price_max:,}\n")

    url = f"https://www.realtor.com/realestateandhomes-search/{request.location}/price-{request.price_min}-{request.price_max}"
    print(f"Loading {url}...")
    checkpoint("Navigate to page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Note: realtor.com may block fresh CDP Chrome profiles
    if any('could not be processed' in l for l in text_lines[:5]):
        print("  WARNING: Request blocked by realtor.com bot detection.")
        print("  The JS/Stagehand version works correctly.")

    listings = []
    i = 0
    while i < len(text_lines) and len(listings) < request.max_results:
        line = text_lines[i]

        if line == 'House for sale' and i + 1 < len(text_lines):
            pm = PRICE_RE.match(text_lines[i + 1])
            if pm:
                price = text_lines[i + 1]
                j = i + 2

                # Skip optional price adjustments like '$500' or '$10k'
                if j < len(text_lines) and PRICE_RE.match(text_lines[j]) and len(text_lines[j]) < 8:
                    j += 1

                bed = 'N/A'
                bath = 'N/A'
                sqft = 'N/A'
                address = 'N/A'

                # Parse bed, bath, sqft
                while j < min(i + 10, len(text_lines)):
                    bm = BED_RE.match(text_lines[j])
                    if bm:
                        bed = bm.group(1)
                        j += 1
                        continue
                    btm = BATH_RE.match(text_lines[j])
                    if btm:
                        bath = btm.group(1)
                        j += 1
                        continue
                    sm = SQFT_RE.match(text_lines[j])
                    if sm:
                        sqft = sm.group(1)
                        j += 1
                        break
                    j += 1

                # Skip 'X square feet' and optional lot lines
                while j < min(i + 15, len(text_lines)):
                    if 'square feet' in text_lines[j] or 'square foot' in text_lines[j] or text_lines[j].endswith('sqft lot'):
                        j += 1
                    else:
                        break

                # Address is the next 2 lines
                if j + 1 < len(text_lines):
                    street = text_lines[j]
                    city_state = text_lines[j + 1]
                    address = f'{street}, {city_state}'

                listings.append(HomeListing(
                    address=address,
                    price=price,
                    bedrooms=bed,
                    bathrooms=bath,
                    sqft=sqft,
                ))

        i += 1

    print("=" * 60)
    loc_label = request.location.replace("_", ", ")
    print(f"Homes for sale in {loc_label}")
    print("=" * 60)
    for idx, r in enumerate(listings, 1):
        print(f"\n{idx}. {r.address}")
        print(f"   Price:     {r.price}")
        print(f"   Bedrooms:  {r.bedrooms}")
        print(f"   Bathrooms: {r.bathrooms}")
        print(f"   Sqft:      {r.sqft}")

    print(f"\nFound {len(listings)} listings")

    return RealtorSearchResult(listings=listings, total_found=len(listings))


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_user_data = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            user_data_dir=chrome_user_data,
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        request = RealtorSearchRequest()
        result = realtor_search(page, request)
        print(f"\nReturned {result.total_found} listings")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)