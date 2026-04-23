"""
Auto-generated Playwright script (Python)
Google Maps – Transit directions

Uses CDP-launched Chrome to avoid bot detection.
Navigates to transit directions URL → extracts route options.
"""

import os, sys, shutil, urllib.parse, re
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class TransitDirectionsRequest:
    origin: str = "Union Station, Los Angeles"
    destination: str = "Santa Monica Pier"


@dataclass
class Route:
    duration: str = ""
    departure_time: str = ""
    arrival_time: str = ""
    transit_lines: List[str] = field(default_factory=list)
    fare: str = ""


@dataclass
class TransitDirectionsResult:
    routes: List[Route] = field(default_factory=list)


def transit_directions(page: Page, request: TransitDirectionsRequest) -> TransitDirectionsResult:
    """Get transit directions from Google Maps."""
    print(f"  Origin:      {request.origin}")
    print(f"  Destination: {request.destination}\n")

    checkpoint("Navigate to Google Maps directions")
    origin = urllib.parse.quote(request.origin)
    dest = urllib.parse.quote(request.destination)
    page.goto(
        f"https://www.google.com/maps/dir/{origin}/{dest}/",
        wait_until="domcontentloaded",
    )
    page.wait_for_timeout(6000)

    checkpoint("Click transit tab")
    # Click the transit mode button (train icon)
    page.evaluate(r"""() => {
        // Transit button has data-travel_mode="3" or img alt="Transit"
        const btns = document.querySelectorAll('[data-travel_mode]');
        for (const btn of btns) {
            if (btn.getAttribute('data-travel_mode') === '3') {
                btn.click();
                return true;
            }
        }
        // Fallback: look for transit icon button
        const imgs = document.querySelectorAll('img[alt*="Transit"], img[alt*="transit"]');
        if (imgs.length > 0) {
            imgs[0].closest('button')?.click();
            return true;
        }
        return false;
    }""")
    page.wait_for_timeout(5000)

    checkpoint("Extract route options")
    routes_data = page.evaluate(r"""() => {
        const trips = document.querySelectorAll('[data-trip-index]');
        const results = [];
        for (const trip of trips) {
            const text = trip.innerText;

            // Times: e.g. "6:48 PM—8:12 PM" - required for transit routes
            let departure = '', arrival = '';
            const timeMatch = text.match(/(\d{1,2}:\d{2}\s*[AP]M)\s*[—–-]\s*(\d{1,2}:\d{2}\s*[AP]M)/);
            if (timeMatch) {
                departure = timeMatch[1];
                arrival = timeMatch[2];
            }
            // Skip non-transit routes (no departure/arrival)
            if (!departure) continue;

            // Duration: e.g. "1 hr 24 min"
            let duration = '';
            const durMatch = text.match(/(\d+\s*hr\s*)?\d+\s*min/);
            if (durMatch) duration = durMatch[0].trim();

            // Transit lines from img alt text or visible line names
            // Look for "Metro X Line", "X Line", or standalone bus numbers
            const transitLines = [];
            // Match "Metro A Line", "B Line", etc.
            const lineMatches = text.matchAll(/(Metro\s+)?([A-Z])\s+Line/g);
            for (const m of lineMatches) {
                const name = m[0].trim();
                if (!transitLines.includes(name)) transitLines.push(name);
            }
            // Match standalone bus route numbers (lines that are just a number, not part of times)
            const textLines = text.split('\n').map(l => l.trim()).filter(Boolean);
            for (const line of textLines) {
                // Bus route numbers like "33", "720", "7" - standalone on a line
                if (/^\d{1,4}$/.test(line)) {
                    const num = line;
                    // Don't include if it's clearly part of a time or duration
                    if (!transitLines.includes(num)) transitLines.push(num);
                }
            }

            // Fare: e.g. "$1.75"
            let fare = '';
            const fareMatch = text.match(/\$[\d.]+/);
            if (fareMatch) fare = fareMatch[0];

            results.push({duration, departure, arrival, transit_lines: transitLines, fare});
        }
        return results;
    }""")

    result = TransitDirectionsResult()
    for rd in routes_data:
        r = Route()
        r.duration = rd.get("duration", "")
        r.departure_time = rd.get("departure", "")
        r.arrival_time = rd.get("arrival", "")
        r.transit_lines = rd.get("transit_lines", [])
        r.fare = rd.get("fare", "")
        result.routes.append(r)

    for i, r in enumerate(result.routes):
        print(f"  Route {i + 1}:")
        print(f"    Duration:    {r.duration}")
        print(f"    Departure:   {r.departure_time}")
        print(f"    Arrival:     {r.arrival_time}")
        print(f"    Lines:       {', '.join(r.transit_lines)}")
        print(f"    Fare:        {r.fare}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("gmaps_transit")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = TransitDirectionsRequest()
            result = transit_directions(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.routes)} routes")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
