"""
Playwright script (Python) — Agoda Hotel Search
Search for hotels by destination and extract listings.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class AgodaSearchRequest:
    destination: str = "Bangkok, Thailand"
    checkin_date: date = None
    checkout_date: date = None
    max_results: int = 5


@dataclass
class HotelItem:
    hotel_name: str = ""
    guest_score: str = ""
    price_per_night: str = ""
    location: str = ""


@dataclass
class AgodaSearchResult:
    destination: str = ""
    items: List[HotelItem] = field(default_factory=list)


# Searches Agoda for hotels in a destination and extracts hotel details.
def search_agoda_hotels(page: Page, request: AgodaSearchRequest) -> AgodaSearchResult:
    """Search Agoda for hotel listings."""
    checkin = request.checkin_date or (date.today() + relativedelta(months=2))
    checkout = request.checkout_date or (checkin + timedelta(days=3))
    ci = checkin.strftime("%Y-%m-%d")
    co = checkout.strftime("%Y-%m-%d")
    nights = (checkout - checkin).days
    print(f"  Destination: {request.destination}")
    print(f"  Check-in: {ci}  Check-out: {co}\n")

    # Build destination slug (e.g. "Bangkok, Thailand" -> "bangkok-th")
    dest_parts = request.destination.lower().split(",")
    city_name = dest_parts[0].strip().replace(" ", "-")
    country_code = ""
    if len(dest_parts) > 1:
        country = dest_parts[1].strip()
        # Common country code mapping
        cc_map = {"thailand": "th", "japan": "jp", "indonesia": "id", "malaysia": "my",
                  "singapore": "sg", "vietnam": "vn", "india": "in", "china": "cn",
                  "south korea": "kr", "philippines": "ph", "united states": "us",
                  "united kingdom": "gb", "france": "fr", "germany": "de", "italy": "it",
                  "spain": "es", "australia": "au", "canada": "ca", "brazil": "br",
                  "mexico": "mx", "uae": "ae", "turkey": "tr", "egypt": "eg"}
        country_code = cc_map.get(country.lower(), country[:2].lower())
    
    slug = f"{city_name}-{country_code}" if country_code else city_name
    url = f"https://www.agoda.com/city/{slug}.html?checkIn={ci}&los={nights}&rooms=1&adults=2&children=0"
    print(f"Loading {url}...")
    checkpoint("Navigate to Agoda hotel search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(12000)

    # Dismiss cookie/popups
    for sel in ['[data-element-name="BtnPair__RejectBtn"]', 'button:has-text("Dismiss")', 'button:has-text("Accept")', '[aria-label="Close"]']:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.evaluate("el => el.click()")
                page.wait_for_timeout(500)
        except Exception:
            pass

    # Scroll to load hotel cards
    for _ in range(5):
        page.evaluate("window.scrollBy(0, 800)")
        page.wait_for_timeout(1000)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    result = AgodaSearchResult(destination=request.destination)

    checkpoint("Extract hotel listings")
    js_code = """(max) => {
        const items = [];
        // Use attribute selector since class names may have hash suffixes
        let cards = document.querySelectorAll('[class*="PropertyCard"], [class*="property-card"], [data-selenium="hotel-item"]');
        // Filter to top-level cards (ones that contain hotel links and have substantial text)
        let candidates = Array.from(cards).filter(c => {
            return c.querySelector('a[href*="/hotel/"]') && c.textContent.length > 100;
        });
        // Deduplicate: remove nested cards (if a card is child of another card)
        candidates = candidates.filter(c => {
            return !candidates.some(other => other !== c && other.contains(c));
        });
        for (const card of candidates) {
            if (items.length >= max) break;
            const text = (card.textContent || '').replace(/\\s+/g, ' ').trim();

            let name = '';
            const nameEl = card.querySelector('a[href*="/hotel/"]');
            if (nameEl) name = nameEl.textContent.trim();

            let stars = '';

            let score = '';
            const scm = text.match(/(\\d\\.\\d|\\d)\\s*(?:Exceptional|Excellent|Very good|Good|Pleasant|Fair)/i);
            if (scm) score = scm[1];

            let price = '';
            const pm = text.match(/(?:USD|US\\$|\\$)\\s*([\\d,]+)/);
            if (pm) price = 'USD ' + pm[1];

            let location = '';
            const innerLines = (card.innerText || '').split('\\n').map(l => l.trim());
            for (const line of innerLines) {
                const lm = line.match(/^([A-Za-z][a-z]+(?:\\s+[A-Za-z][a-z]+)*),\\s*Bangkok/);
                if (lm) { location = lm[1] + ', Bangkok'; break; }
            }

            if (name && name.length > 2) {
                items.push({hotel_name: name, guest_score: score, price_per_night: price, location: location});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = HotelItem()
        item.hotel_name = d.get("hotel_name", "")
        item.guest_score = d.get("guest_score", "")
        item.price_per_night = d.get("price_per_night", "")
        item.location = d.get("location", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} hotels in '{request.destination}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.hotel_name}")
        print(f"     Score:    {item.guest_score}")
        print(f"     Price:    {item.price_per_night}/night")
        print(f"     Location: {item.location}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("agoda")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = AgodaSearchRequest()
            result = search_agoda_hotels(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} hotels")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
