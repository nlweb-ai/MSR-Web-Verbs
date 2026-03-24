"""
Auto-generated Playwright script (Python)
Redfin Rental Search: Redmond, WA with price filter ($1500-$3000)

Generated on: 2026-02-24T17:54:17.204Z
Recorded 22 browser interactions
Note: This script was generated using AI-driven discovery patterns

Uses Playwright persistent context with real Chrome Default profile.
IMPORTANT: Close ALL Chrome windows before running!
"""

import re
import os
import tempfile
import shutil
from playwright.sync_api import Page, sync_playwright, expect

from dataclasses import dataclass
import subprocess
import json
import time
from urllib.request import urlopen

import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import find_chrome_executable, get_free_port


def extract_listings(page, max_listings=5):
    """Extract apartment rental listings from the current search results page."""
    listings = []
    seen_addresses = set()

    # Try common Redfin rental card selectors
    card_selectors = [
        "[data-rf-test-id='photo-card']",
        ".RentalHomeCard",
        ".HomeCard",
        "[class*='HomeCard']",
        "[class*='RentalCard']",
        "[class*='rental-card']",
        ".MapHomeCard",
    ]

    cards = None
    for sel in card_selectors:
        found = page.locator(sel)
        if found.count() > 0:
            cards = found
            break

    if not cards or cards.count() == 0:
        print("Warning: Could not find listing cards on the page.")
        return listings

    total = cards.count()
    for i in range(total):
        if len(listings) >= max_listings:
            break
        card = cards.nth(i)
        try:
            text = card.inner_text(timeout=3000)
            lines = [l.strip() for l in text.split("\n") if l.strip()]

            listing = {}

            # --- Extract price (e.g. "$1,879+/mo", "Studio: $2,060") ---
            for line in lines:
                if re.search(r"\$[\d,]+", line) and "price" not in listing:
                    listing["price"] = line.strip()
                    break

            # --- Extract address from dedicated element ---
            address = None
            try:
                addr_el = card.locator(
                    "[class*='address' i], [class*='Address'], "
                    "[data-rf-test-id='abp-homeinfo-homeAddress'], "
                    "[class*='homecardV2__address' i]"
                ).first
                if addr_el.is_visible(timeout=1000):
                    address = addr_el.inner_text(timeout=1000).strip()
            except Exception:
                pass

            # Fallback: look for a line that looks like a street address
            if not address:
                for line in lines:
                    if re.search(r"\d+\s+\w+\s+(St|Ave|Blvd|Dr|Rd|Ln|Ct|Cir|Way|Pl)", line, re.IGNORECASE):
                        address = line.strip()
                        break

            # Fallback: try the property name (first meaningful line)
            if not address:
                for line in lines:
                    if (not re.search(r"^\$", line)
                            and not re.search(r"(WALKTHROUGH|ABOUT|FREE|WEEKS)", line, re.IGNORECASE)
                            and len(line) > 3):
                        address = line.strip()
                        break

            # Clean up address: remove newlines and pipe separators
            if address:
                address = re.sub(r"\s*\n\s*\|?\s*", ", ", address).strip(", ")
            listing["address"] = address or "N/A"

            # Deduplicate by address
            addr_key = listing["address"].lower().strip()
            if addr_key in seen_addresses:
                continue
            seen_addresses.add(addr_key)

            # --- Extract beds / baths / sqft ---
            for line in lines:
                # Only match short lines for beds/baths/sqft to avoid description text
                if len(line) > 80:
                    continue
                if re.search(r"\d+\s*(bed|bd)", line, re.IGNORECASE) and "beds" not in listing:
                    listing["beds"] = line.strip()
                elif re.search(r"\d+\s*(bath|ba)", line, re.IGNORECASE) and "baths" not in listing:
                    listing["baths"] = line.strip()
                elif re.search(r"[\d,]+\s*sq\s*ft", line, re.IGNORECASE) and "sqft" not in listing:
                    listing["sqft"] = line.strip()

            listings.append(listing)
        except Exception as e:
            print(f"Warning: Could not extract listing {i + 1}: {e}")

    return listings


@dataclass(frozen=True)
class RedfinSearchRequest:
    location: str
    max_results: int


@dataclass(frozen=True)
class RedfinHome:
    address: str
    price: str
    beds: str
    sqft: str


@dataclass(frozen=True)
class RedfinSearchResult:
    location: str
    homes: list[RedfinHome]


# Searches Redfin for homes for sale in a location and returns up to max_results listings.

def search_redfin_homes(page: Page, request: RedfinSearchRequest) -> RedfinSearchResult:
    raw = []
    try:
        query = request.location.replace(" ", "%20").replace(",", "%2C")
        url = f"https://www.redfin.com/city/16163/WA/Seattle/apartments-for-rent"
        print(f"Navigating to Redfin rentals for {request.location}...")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(5000)
        for _ in range(3):
            page.evaluate("window.scrollBy(0, 600)")
            page.wait_for_timeout(800)
        raw = extract_listings(page, request.max_results)
    except Exception as e:
        print(f"Error: {e}")
    return RedfinSearchResult(
        location=request.location,
        homes=[RedfinHome(
            address=r.get("address","N/A"), price=r.get("price","N/A"),
            beds=r.get("beds","N/A"), sqft=r.get("sqft","N/A"),
        ) for r in raw],
    )


def test_search_redfin_homes() -> None:
    from datetime import date
    today = date.today()

    request = RedfinSearchRequest(
        location="Seattle, WA",
        max_results=5,
    )
    port = get_free_port()
    profile_dir = tempfile.mkdtemp(prefix="chrome_cdp_")
    chrome = os.environ.get("CHROME_PATH") or find_chrome_executable()
    chrome_proc = subprocess.Popen(
        [
            chrome,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={profile_dir}",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1280,987",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    ws_url = None
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            resp = urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2)
            ws_url = json.loads(resp.read()).get("webSocketDebuggerUrl", "")
            if ws_url:
                break
        except Exception:
            pass
        time.sleep(0.4)
    if not ws_url:
        raise TimeoutError("Chrome CDP not ready")
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_redfin_homes(page, request)
        finally:
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)
    assert isinstance(result, RedfinSearchResult)
    assert len(result.homes) <= request.max_results
    print(f'\nFound {len(result.homes)} homes')
    for i, item in enumerate(result.homes, 1):
        print(f'  {i}. {item.address}')


if __name__ == "__main__":
    test_search_redfin_homes()
