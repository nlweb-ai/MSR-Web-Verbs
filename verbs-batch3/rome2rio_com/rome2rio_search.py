"""
Rome2Rio - Travel Route Search
Search for travel routes between cities and extract transport options
with duration and price information.
"""

import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


TRANSPORT_TYPES = {'train', 'rideshare', 'bus', 'plane', 'car'}
DURATION_RE = re.compile(r'^\d+h(?:\s+\d+m)?$')
PRICE_RE = re.compile(r'^\$[\d,]+')


@dataclass(frozen=True)
class Rome2rioSearchRequest:
    origin: str = "Paris"
    destination: str = "Amsterdam"
    max_results: int = 5


@dataclass(frozen=True)
class TravelRoute:
    mode: str = ""
    duration: str = ""
    price: str = ""


@dataclass(frozen=True)
class Rome2rioSearchResult:
    origin: str = ""
    destination: str = ""
    routes: tuple = ()


# Search rome2rio.com for travel routes between two cities and return
# transport options with mode, estimated duration, and price range.
def rome2rio_search(page: Page, request: Rome2rioSearchRequest) -> Rome2rioSearchResult:
    origin = request.origin
    destination = request.destination
    max_results = request.max_results
    print(f"  From: {origin} To: {destination}\n")

    url = f"https://www.rome2rio.com/s/{origin}/{destination}"
    print(f"Loading {url}...")
    checkpoint("Navigate to page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    routes = []

    # Skip to route options (after 'Select an option below')
    i = 0
    while i < len(text_lines):
        if 'Select an option below' in text_lines[i]:
            i += 1
            break
        i += 1

    while i < len(text_lines) and len(routes) < max_results:
        line = text_lines[i]

        if line in TRANSPORT_TYPES:
            # Look back for mode name
            mode = 'Unknown'
            for j in range(i - 1, max(i - 5, 0), -1):
                t = text_lines[j]
                if t in ('Train', 'Rideshare', 'Bus', 'Fly') or t.startswith('Drive'):
                    mode = t
                    break

            # Look forward for duration and price
            duration = 'N/A'
            price = 'N/A'
            for j in range(i + 1, min(i + 5, len(text_lines))):
                if DURATION_RE.match(text_lines[j]) and duration == 'N/A':
                    duration = text_lines[j]
                if PRICE_RE.match(text_lines[j]):
                    price = text_lines[j]
                    break

            routes.append(TravelRoute(
                mode=mode,
                duration=duration,
                price=price,
            ))

        i += 1

    print("=" * 60)
    print(f"Travel: {origin} to {destination}")
    print("=" * 60)
    for idx, r in enumerate(routes, 1):
        print(f"\n{idx}. {r.mode}")
        print(f"   Duration: {r.duration}")
        print(f"   Price:    {r.price}")

    print(f"\nFound {len(routes)} routes")

    return Rome2rioSearchResult(
        origin=origin,
        destination=destination,
        routes=tuple(routes),
    )


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_profile = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default",
    )
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            chrome_profile,
            headless=False,
            channel="chrome",
        )
        page = context.pages[0] if context.pages else context.new_page()
        request = Rome2rioSearchRequest()
        result = rome2rio_search(page, request)
        print(f"\nResult: {result}")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)