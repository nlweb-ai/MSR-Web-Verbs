"""
Auto-generated Playwright script (Python)
AllEvents – Event Search
City: "Austin", Query: "music festival"

Generated on: 2026-04-18T04:39:38.457Z
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
class EventSearchRequest:
    city: str = "Austin"
    query: str = "music festival"
    max_results: int = 5


@dataclass
class Event:
    event_name: str = ""
    date: str = ""
    venue: str = ""
    event_url: str = ""


@dataclass
class EventSearchResult:
    events: list = field(default_factory=list)


def allevents_search(page: Page, request: EventSearchRequest) -> EventSearchResult:
    """Search AllEvents for events."""
    print(f"  City: {request.city}")
    print(f"  Query: {request.query}\n")

    search_url = f"https://allevents.in/{request.city.lower()}?q={quote_plus(request.query)}"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to AllEvents search")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Dismiss popups
    for sel in ["button:has-text('Accept')", "button:has-text('Got it')", "button[aria-label='Close']"]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(500)
        except Exception:
            pass

    # Extract events
    checkpoint("Extract events")
    events = page.evaluate(r"""(maxResults) => {
        const results = [];
        const cards = document.querySelectorAll(
            '.event-card, .item, article, [itemtype*="Event"], .event-item, a[href*="/e/"]'
        );
        const seen = new Set();
        for (const card of cards) {
            if (results.length >= maxResults) break;
            const nameEl = card.querySelector('h2, h3, h4, .event-title, .title, [itemprop="name"]');
            const dateEl = card.querySelector('time, .event-date, .date, [itemprop="startDate"], .when');
            const venueEl = card.querySelector('.venue, .location, [itemprop="location"], .where');
            const linkEl = card.tagName === 'A' ? card : card.querySelector('a[href*="/e/"]') || card.querySelector('a');

            const name = nameEl ? nameEl.innerText.trim() : (card.tagName === 'A' ? card.innerText.split('\n')[0].trim() : '');
            if (!name || name.length < 3 || seen.has(name)) continue;
            seen.add(name);

            const date = dateEl ? dateEl.innerText.trim() : '';
            const venue = venueEl ? venueEl.innerText.trim() : '';
            const url = linkEl ? linkEl.href : '';

            results.push({ event_name: name, date, venue, event_url: url });
        }
        return results;
    }""", request.max_results)

    print("\n" + "=" * 60)
    print(f"AllEvents: {request.query} in {request.city}")
    print("=" * 60)
    for idx, e in enumerate(events, 1):
        print(f"\n  {idx}. {e['event_name']}")
        print(f"     Date: {e['date']}")
        print(f"     Venue: {e['venue']}")
        print(f"     URL: {e['event_url']}")

    result_events = [Event(**e) for e in events]
    print(f"\nFound {len(result_events)} events")
    return EventSearchResult(events=result_events)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("allevents_in")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = allevents_search(page, EventSearchRequest())
            print(f"\nReturned {len(result.events)} events")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
