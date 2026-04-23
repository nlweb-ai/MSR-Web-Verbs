"""
Playwright script (Python) — Kayak Flight Search
Search Kayak for flights between cities.
"""
import os, sys
os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class KayakRequest:
    origin: str = "Boston"
    destination: str = "London"
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
class KayakResult:
    origin: str = ""
    destination: str = ""
    items: List[FlightItem] = field(default_factory=list)


def search_kayak(page: Page, request: KayakRequest) -> KayakResult:
    import urllib.parse
    depart = datetime.now() + timedelta(days=30)
    ret = depart + timedelta(days=7)
    url = f"https://www.kayak.com/flights/{request.origin}-{request.destination}/{depart.strftime('%Y-%m-%d')}/{ret.strftime('%Y-%m-%d')}?sort=bestflight_a"
    print(f"Loading {url}...")
    checkpoint("Navigate to flight results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = KayakResult(origin=request.origin, destination=request.destination)

    checkpoint("Extract flight listings")
    js_code = """(max) => {
        const results = [];
        const cards = document.querySelectorAll('[class*="resultInner"], [class*="nrc6-inner"], [class*="result-item"]');
        for (const card of cards) {
            if (results.length >= max) break;
            const text = (card.textContent || '').replace(/\\s+/g, ' ');
            if (text.length < 20) continue;

            let airline = '';
            const airEl = card.querySelector('[class*="codeshares"], [class*="airline"], img[alt]');
            if (airEl) airline = airEl.textContent?.trim() || airEl.getAttribute('alt') || '';

            let departure = '', arrival = '';
            const timeEls = card.querySelectorAll('[class*="time"], [class*="depart"], [class*="arrive"]');
            if (timeEls.length >= 2) {
                departure = timeEls[0].textContent.trim();
                arrival = timeEls[1].textContent.trim();
            }

            let duration = '';
            const durEl = card.querySelector('[class*="duration"], [class*="segment-duration"]');
            if (durEl) duration = durEl.textContent.trim();

            let stops = '';
            const stopEl = card.querySelector('[class*="stops"], [class*="stop-info"]');
            if (stopEl) stops = stopEl.textContent.trim();

            let price = '';
            const priceEl = card.querySelector('[class*="price"], [class*="Price"]');
            if (priceEl) price = priceEl.textContent.trim();

            if (!price && !airline) continue;
            results.push({ airline, departure, arrival, duration, stops, price });
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

    print(f"\nFound {len(result.items)} flights {request.origin} → {request.destination}:")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.airline}")
        print(f"     {item.departure} → {item.arrival}  Duration: {item.duration}")
        print(f"     Stops: {item.stops}  Price: {item.price}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("kayak")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_kayak(page, KayakRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} flights")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
