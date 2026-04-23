"""
Auto-generated Playwright script (Python)
Bandsintown – Concert Search
Artist: "Beyonce"

Generated on: 2026-04-18T04:52:46.212Z
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
class ConcertRequest:
    artist: str = "Beyonce"
    max_events: int = 5


@dataclass
class Concert:
    venue: str = ""
    city: str = ""
    date: str = ""
    ticket_url: str = ""


@dataclass
class ConcertResult:
    events: list = field(default_factory=list)


def bandsintown_search(page: Page, request: ConcertRequest) -> ConcertResult:
    """Search Bandsintown for upcoming concerts by an artist."""
    print(f"  Artist: {request.artist}\n")

    # ── Step 1: Go to Bandsintown and search ──────────────────────────
    print("Loading https://www.bandsintown.com ...")
    checkpoint("Navigate to Bandsintown homepage")
    page.goto("https://www.bandsintown.com", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Type into search bar
    search = page.locator('input[aria-label="Search Bar"]')
    search.click()
    page.wait_for_timeout(500)
    search.press("Control+a")
    search.type(request.artist, delay=50)
    page.wait_for_timeout(2000)

    # ── Step 2: Click the first artist from autocomplete ──────────────
    checkpoint("Click artist from search results")
    artist_link = page.locator('a[href*="/a/"]').first
    if artist_link.count() > 0:
        artist_link.click()
        page.wait_for_timeout(5000)
    else:
        print("No artist results found.")
        return ConcertResult()

    # ── Step 3: Extract upcoming events ───────────────────────────────
    checkpoint("Extract upcoming events")
    events_data = page.evaluate(r"""(maxEvents) => {
        const text = document.body.innerText;
        const results = [];

        // Check for "No upcoming shows"
        const noShows = text.includes('No upcoming shows');

        // Try to find event listings - look for date/venue/city patterns
        // Events are listed with month/day, year, city, state, venue
        const eventBlocks = document.querySelectorAll('[data-testid*="event"], [class*="event-listing"], [class*="eventList"] a, a[href*="/e/"]');
        const seen = new Set();
        for (const block of eventBlocks) {
            if (results.length >= maxEvents) break;
            const blockText = block.innerText.trim();
            if (!blockText || blockText.length < 5 || seen.has(blockText)) continue;
            seen.add(blockText);

            // Parse event text - typically "MON DD YYYY\nCity, ST\nVenue"
            const lines = blockText.split('\n').map(l => l.trim()).filter(l => l);
            let date = '', city = '', venue = '';
            for (const line of lines) {
                if (/^(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\b/i.test(line) || /^\d{1,2}$/.test(line) || /^\d{4}$/.test(line)) {
                    date += (date ? ' ' : '') + line;
                } else if (/,\s*[A-Z]{2}$/i.test(line)) {
                    city = line;
                } else if (line.length > 2 && !line.includes('Tickets') && !line.includes('I Was There') && !line.includes('Follow')) {
                    if (!venue) venue = line;
                }
            }
            if (venue || city) {
                results.push({
                    venue: venue,
                    city: city,
                    date: date.trim(),
                    ticket_url: block.href || '',
                });
            }
        }

        // Fallback: parse from body text
        if (results.length === 0 && !noShows) {
            const regex = /(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+\d{1,2}\s+\d{4}\s*\n\s*([^\n]+)\s*\n\s*([^\n]+)/gi;
            let match;
            while ((match = regex.exec(text)) !== null && results.length < maxEvents) {
                results.push({
                    venue: match[3].trim(),
                    city: match[2].trim(),
                    date: match[1].trim() + ' ' + match[0].match(/\d{1,2}/)[0] + ', ' + match[0].match(/\d{4}/)[0],
                    ticket_url: '',
                });
            }
        }

        return { events: results, noShows };
    }""", request.max_events)

    events = events_data.get("events", [])
    no_shows = events_data.get("noShows", False)

    result = ConcertResult(
        events=[Concert(venue=e['venue'], city=e['city'], date=e['date'], ticket_url=e['ticket_url']) for e in events]
    )

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Bandsintown: {request.artist}")
    print("=" * 60)
    if no_shows and not events:
        print("  No upcoming shows found.")
        # Show past events if any
        past_text = page.evaluate(r"""() => {
            const text = document.body.innerText;
            const pastIdx = text.indexOf('Past');
            if (pastIdx >= 0) {
                return text.slice(pastIdx, pastIdx + 500);
            }
            return '';
        }""")
        if past_text:
            print(f"\n  Recent past events:")
            print(f"  {past_text[:300]}")
    else:
        for i, e in enumerate(events, 1):
            print(f"\n  {i}. {e['venue']}")
            print(f"     City: {e['city']}")
            print(f"     Date: {e['date']}")
            if e['ticket_url']:
                print(f"     Tickets: {e['ticket_url']}")
    print(f"\n  Total: {len(result.events)} upcoming events")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("bandsintown_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = bandsintown_search(page, ConcertRequest())
            print(f"\nReturned {len(result.events)} events")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
