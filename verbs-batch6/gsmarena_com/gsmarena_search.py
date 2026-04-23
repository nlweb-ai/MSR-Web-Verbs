"""
Auto-generated Playwright script (Python)
GSMArena – Phone Specs
Query: "Samsung Galaxy S24"

Generated on: 2026-04-18T05:31:58.948Z
Recorded 3 browser interactions
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
class PhoneRequest:
    query: str = "Samsung Galaxy S24"


@dataclass
class PhoneResult:
    name: str = ""
    display_size: str = ""
    processor: str = ""
    ram: str = ""
    battery: str = ""
    camera: str = ""
    price: str = ""


def gsmarena_search(page: Page, request: PhoneRequest) -> PhoneResult:
    """Search GSMArena for phone specs."""
    print(f"  Query: {request.query}\n")

    # ── Step 1: Search for the phone ──────────────────────────────────
    search_url = f"https://www.gsmarena.com/results.php3?sQuickSearch=yes&sName={quote_plus(request.query)}"
    print("Searching GSMArena...")
    checkpoint("Navigate to GSMArena search")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # ── Step 2: Click the first result ────────────────────────────────
    checkpoint("Get first search result")
    first_result = page.evaluate(r"""() => {
        const link = document.querySelector('.makers a');
        return link ? { text: link.innerText.trim(), href: link.href } : null;
    }""")

    if not first_result:
        print("  No search results found.")
        return PhoneResult(name=request.query)

    phone_name = first_result['text'].replace('\n', ' ')
    print(f"  Found: {phone_name}")
    print(f"  Navigating to specs page...")

    page.goto(first_result['href'], wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # ── Step 3: Extract specs ─────────────────────────────────────────
    checkpoint("Extract phone specs")
    specs = page.evaluate(r"""() => {
        const result = {};
        const tables = document.querySelectorAll('#specs-list table');
        for (const table of tables) {
            const rows = table.querySelectorAll('tr');
            for (const row of rows) {
                const label = (row.querySelector('.ttl a') || row.querySelector('.ttl'))?.innerText?.trim() || '';
                const value = row.querySelector('.nfo')?.innerText?.trim() || '';
                if (label && value) result[label] = value;
            }
        }
        return result;
    }""")

    # Map to required fields
    display = specs.get('Size', '')
    processor = specs.get('Chipset', '')
    ram = specs.get('Internal', '')
    battery = specs.get('Type', '')
    camera = specs.get('Quad', specs.get('Triple', specs.get('Dual', specs.get('Single', ''))))
    # Extract main camera resolution (first line)
    if camera:
        camera = camera.split('\n')[0].strip()
    price = specs.get('Price', '')

    result = PhoneResult(
        name=phone_name, display_size=display, processor=processor,
        ram=ram, battery=battery, camera=camera, price=price
    )

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"GSMArena: {phone_name}")
    print("=" * 60)
    print(f"  Display:   {display}")
    print(f"  Processor: {processor}")
    print(f"  RAM:       {ram}")
    print(f"  Battery:   {battery}")
    print(f"  Camera:    {camera}")
    print(f"  Price:     {price}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("gsmarena_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = gsmarena_search(page, PhoneRequest())
            print(f"\nReturned specs for {result.name}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
