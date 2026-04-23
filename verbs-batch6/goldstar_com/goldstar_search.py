"""
Auto-generated Playwright script (Python)
Goldstar – Discount Event Tickets
Location: "New York"

Generated on: 2026-04-18T05:28:47.839Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class EventRequest:
    location: str = "New York"
    max_results: int = 5


@dataclass
class Event:
    name: str = ""
    venue: str = ""
    date: str = ""
    original_price: str = ""
    discount_price: str = ""


@dataclass
class EventResult:
    events: list = field(default_factory=list)


def goldstar_search(page: Page, request: EventRequest) -> EventResult:
    """Search Goldstar for discount events."""
    print(f"  Location: {request.location}\n")

    url = "https://www.goldstar.com/new-york"
    print(f"Loading {url}...")
    checkpoint("Navigate to Goldstar")
    page.goto(url, wait_until="domcontentloaded")

    # Wait for event listings to load (CSR)
    for attempt in range(10):
        page.wait_for_timeout(3000)
        body_len = page.evaluate("document.body.innerText.length")
        print(f"  Poll {attempt+1}: bodyLen={body_len}")
        if body_len > 5000:
            break
        page.evaluate("window.scrollBy(0, 400)")

    # Scroll to trigger lazy loading
    for _ in range(8):
        page.evaluate("window.scrollBy(0, 600)")
        page.wait_for_timeout(1000)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    checkpoint("Extract event listings")
    items_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();

        // Find show links: /nyc/shows/{id}-{name}
        const links = document.querySelectorAll('a[href*="/shows/"]');
        for (const a of links) {
            if (results.length >= maxResults) break;
            const href = a.getAttribute('href') || '';
            if (!/\/shows\/\d+/.test(href)) continue;

            const block = a.closest('article, li, section, [class*="card"], [class*="event"]') || a;
            // Get name from img alt, aria-label, or link text
            let name = '';
            const img = block.querySelector('img[alt]');
            if (img) name = img.getAttribute('alt') || '';
            if (!name) name = a.getAttribute('aria-label') || '';
            if (!name) {
                // Get first meaningful line of text
                const text = a.innerText.trim();
                const lines = text.split('\n').filter(l => l.trim().length > 3);
                name = lines[0] || '';
            }
            name = name.trim();
            if (!name || name.length < 3 || seen.has(name)) continue;
            if (/^(flash sale|off-broadway|trending|deals|menu|sign)/i.test(name)) continue;
            seen.add(name);

            const text = block.innerText || '';
            let venue = '', date = '', original_price = '', discount_price = '';

            // Extract rating percentage
            const ratM = text.match(/(\d+)%/);
            const rating = ratM ? ratM[1] + '%' : '';

            // Extract prices
            const prices = text.match(/\$(\d[\d,.]*)/g) || [];
            if (prices.length >= 2) {
                original_price = prices[0];
                discount_price = prices[1];
            } else if (prices.length === 1) {
                discount_price = prices[0];
            }

            results.push({ name: name.slice(0, 120), venue, date, original_price, discount_price });
        }
        return results;
    }""", request.max_results)

    result = EventResult(events=[Event(**e) for e in items_data])

    print("\n" + "=" * 60)
    print(f"Goldstar: {request.location}")
    print("=" * 60)
    for e in result.events:
        print(f"  {e.name}")
        print(f"    Venue: {e.venue}  Date: {e.date}")
        print(f"    Price: {e.original_price} -> {e.discount_price}")
    print(f"\n  Total: {len(result.events)} events")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("goldstar_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = goldstar_search(page, EventRequest())
            print(f"\nReturned {len(result.events)} events")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
