"""
Playwright script (Python) — Google Flights Search
Search for flights on Google Flights.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GoogleFlightsRequest:
    origin: str = "SFO"
    destination: str = "JFK"
    date: str = ""  # YYYY-MM-DD, defaults to ~1 month from now
    max_results: int = 5


@dataclass
class FlightItem:
    airline: str = ""
    departure: str = ""
    arrival: str = ""
    duration: str = ""
    stops: str = ""
    price: str = ""


@dataclass
class GoogleFlightsResult:
    origin: str = ""
    destination: str = ""
    items: List[FlightItem] = field(default_factory=list)


# Searches Google Flights for one-way flights and returns up to max_results
# options with airline, departure/arrival times, duration, stops, and price.
def search_google_flights(page: Page, request: GoogleFlightsRequest) -> GoogleFlightsResult:
    import urllib.parse
    from datetime import datetime, timedelta

    date_str = request.date
    if not date_str:
        d = datetime.now() + timedelta(days=30)
        date_str = d.strftime("%Y-%m-%d")

    url = f"https://www.google.com/travel/flights?q=Flights%20from%20{urllib.parse.quote_plus(request.origin)}%20to%20{urllib.parse.quote_plus(request.destination)}%20on%20{date_str}%20one%20way"
    print(f"Loading {url}...")
    checkpoint("Navigate to flight results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = GoogleFlightsResult(origin=request.origin, destination=request.destination)

    checkpoint("Extract flight listings")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        const rows = document.querySelectorAll('.yR1fYc');
        for (const row of rows) {
            if (results.length >= max) break;
            const lines = row.innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 7) continue;
            // Structure: departure, -, arrival, airline, duration, route, stops, CO2, emissions, ?, ?, price
            const departure = lines[0].trim();
            const arrival = lines[2].trim();
            const airline = lines[3].trim();
            const duration = lines[4].trim();
            const stops = lines[6].trim();
            // Price is last line starting with $
            let price = '';
            for (let i = lines.length - 1; i >= 0; i--) {
                if (lines[i].trim().startsWith('$')) { price = lines[i].trim(); break; }
            }
            const key = departure + airline + arrival;
            if (seen.has(key)) continue;
            seen.add(key);
            results.push({airline, departure, arrival, duration, stops, price});
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = FlightItem()
        item.airline = d.get("airline", "")
        item.departure = d.get("departure", "")
        item.arrival = d.get("arrival", "")
        item.duration = d.get("duration", "")
        item.stops = d.get("stops", "")
        item.price = d.get("price", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} flights ({request.origin} -> {request.destination}):")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.airline}")
        print(f"     {item.departure} -> {item.arrival}  Duration: {item.duration}")
        print(f"     Stops: {item.stops}  Price: {item.price}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("gflights")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_google_flights(page, GoogleFlightsRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} flights")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
