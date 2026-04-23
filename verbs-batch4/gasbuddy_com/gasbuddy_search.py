import re
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class GasBuddySearchRequest:
    location: str = "Denver, CO"
    max_results: int = 5

@dataclass(frozen=True)
class GasStation:
    station_name: str = ""
    address: str = ""
    regular_price: str = ""
    last_updated: str = ""

@dataclass(frozen=True)
class GasBuddySearchResult:
    stations: list = None  # list[GasStation]

# Search for gas prices near a location on GasBuddy and extract
# station name, address, regular price, and last updated time.
def gasbuddy_search(page: Page, request: GasBuddySearchRequest) -> GasBuddySearchResult:
    location = request.location
    max_results = request.max_results
    print(f"  Location: {location}")
    print(f"  Max results: {max_results}\n")

    url = f"https://www.gasbuddy.com/home?search={quote_plus(location)}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to {url}")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""

    results = []

    # Try structured extraction via individual station card elements
    # Use stationListItem class — each station has exactly one of these
    cards = page.locator('[class*="stationListItem"]')
    count = cards.count()
    print(f"  Found {count} station cards")

    if count > 0:
        for i in range(min(count, max_results)):
            card = cards.nth(i)
            try:
                card_text = card.inner_text(timeout=3000).strip()
                lines = [l.strip() for l in card_text.split("\n") if l.strip()]

                station_name = "N/A"
                address = "N/A"
                regular_price = "N/A"
                last_updated = "N/A"

                # Card text lines (after stripping blanks):
                #   0: station name (e.g. "Costco ")
                #   1: rating number (e.g. "115")
                #   2: street address (e.g. "4741 N Airport WayE")
                #   3: city, state (e.g. "Denver, CO")
                #   4: price (e.g. "$3.29")
                #   5: reporter (e.g. " Owner")
                #   6: time (e.g. "10 Hours Ago")
                for line in lines:
                    # Price
                    pm = re.match(r'^\$(\d+\.\d{2,3})$', line)
                    if pm and regular_price == "N/A":
                        regular_price = "$" + pm.group(1)
                        continue
                    # Last updated
                    if re.search(r'(ago|hour|min|day|just now)', line, re.IGNORECASE) and last_updated == "N/A":
                        last_updated = line
                        continue
                    # City, State — append to address
                    if re.match(r'^[A-Z][a-z]+.*,\s*[A-Z]{2}$', line) and address != "N/A":
                        address += ", " + line
                        continue
                    # Street address
                    if re.search(r'\d', line) and re.search(r'[A-Za-z]', line) and len(line) > 5 and address == "N/A":
                        # Skip pure rating numbers like "115"
                        if not re.match(r'^\d+$', line):
                            address = line
                            continue
                    # Station name — first text-like line
                    if len(line) > 1 and station_name == "N/A" and not re.match(r'^\d+$', line):
                        station_name = line.strip()

                if station_name != "N/A":
                    results.append(GasStation(
                        station_name=station_name,
                        address=address,
                        regular_price=regular_price,
                        last_updated=last_updated,
                    ))
            except Exception:
                continue

    # Fallback: text-based extraction from body text
    # Body text pattern per station: number, address, city/state, $price, username, time ago
    if not results:
        print("  Card selectors missed, trying text-based extraction...")
        text_lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        i = 0
        while i < len(text_lines) and len(results) < max_results:
            line = text_lines[i]
            # Look for a price line as anchor — "$X.XX"
            pm = re.match(r'^\$(\d+\.\d{2,3})$', line)
            if pm:
                regular_price = "$" + pm.group(1)
                station_name = "N/A"
                address = "N/A"
                last_updated = "N/A"

                # Address is usually 2 lines before price
                if i >= 2:
                    addr_line = text_lines[i - 2]
                    city_line = text_lines[i - 1]
                    if re.search(r'\d', addr_line):
                        address = addr_line
                        if re.match(r'^[A-Z].*,\s*[A-Z]{2}$', city_line):
                            address += ", " + city_line

                # Last updated is usually 2 lines after price
                if i + 2 < len(text_lines):
                    updated_line = text_lines[i + 2]
                    if re.search(r'(ago|hour|min|day|just now)', updated_line, re.IGNORECASE):
                        last_updated = updated_line

                # Station name: scan upward past address/number lines
                for back in range(i - 3, max(i - 8, -1), -1):
                    candidate = text_lines[back]
                    if (len(candidate) > 2 and not re.match(r'^\d+$', candidate)
                            and not re.match(r'^\$', candidate)
                            and not re.search(r',\s*[A-Z]{2}$', candidate)):
                        station_name = candidate
                        break

                if station_name != "N/A":
                    results.append(GasStation(
                        station_name=station_name,
                        address=address,
                        regular_price=regular_price,
                        last_updated=last_updated,
                    ))
            i += 1

        results = results[:max_results]

    print("=" * 60)
    print(f"GasBuddy - Gas Prices near \"{location}\"")
    print("=" * 60)
    for idx, s in enumerate(results, 1):
        print(f"\n{idx}. {s.station_name}")
        print(f"   Address: {s.address}")
        print(f"   Regular Price: {s.regular_price}")
        print(f"   Last Updated: {s.last_updated}")

    print(f"\nFound {len(results)} stations")

    return GasBuddySearchResult(stations=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = gasbuddy_search(page, GasBuddySearchRequest())
        print(f"\nReturned {len(result.stations or [])} stations")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
