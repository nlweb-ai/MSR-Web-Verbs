"""
Auto-generated Playwright script (Python)
Time and Date – Look Up Current Time
City: "Tokyo"

Generated on: 2026-04-18T02:30:27.293Z
Recorded 3 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class TimeRequest:
    city: str = "Tokyo"


@dataclass
class TimeResult:
    city_name: str = ""
    current_time: str = ""
    date: str = ""
    timezone_abbr: str = ""
    utc_offset: str = ""


def time_lookup(page: Page, request: TimeRequest) -> TimeResult:
    """Look up the current time for a city on timeanddate.com."""
    print(f"  City: {request.city}\n")

    # ── Search ────────────────────────────────────────────────────────
    search_url = f"https://www.timeanddate.com/worldclock/results.html?query={quote_plus(request.city)}"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to search results")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # ── Find first city link ──────────────────────────────────────────
    city_url = page.evaluate(r"""(cityName) => {
        const links = document.querySelectorAll('table.zebra tr td a');
        for (const link of links) {
            if (link.href && link.href.includes('/worldclock/')) {
                return link.href;
            }
        }
        return null;
    }""", request.city)

    if not city_url:
        print("No city found!")
        return TimeResult()

    print(f"City page: {city_url}")
    checkpoint("Navigate to city page")
    page.goto(city_url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # ── Extract time data ─────────────────────────────────────────────
    data = page.evaluate(r"""() => {
        const ct = document.querySelector('#ct');
        const cta = document.querySelector('#cta');
        const ctdat = document.querySelector('#ctdat');
        const title = document.title;
        const cityMatch = title.match(/Current Local Time in (.+)/);
        const utcMatch = document.body.innerText.match(/UTC\/GMT\s*([+-]?\d+\s*hours?)/i);
        return {
            city_name: cityMatch ? cityMatch[1] : '',
            current_time: ct ? ct.innerText.trim() : '',
            date: ctdat ? ctdat.innerText.trim() : '',
            timezone_abbr: cta ? cta.innerText.trim() : '',
            utc_offset: utcMatch ? utcMatch[0] : '',
        };
    }""")

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Current Time: {request.city}")
    print("=" * 60)
    print(f"  City: {data['city_name']}")
    print(f"  Time: {data['current_time']}")
    print(f"  Date: {data['date']}")
    print(f"  Timezone: {data['timezone_abbr']}")
    print(f"  UTC Offset: {data['utc_offset']}")

    return TimeResult(**data)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("timeanddate_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = time_lookup(page, TimeRequest())
            print(f"\nResult: {result}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
