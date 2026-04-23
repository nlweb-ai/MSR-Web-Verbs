"""
Auto-generated Playwright script (Python)
SpaceWeatherLive – Current Conditions

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass
class SpaceWeatherResult:
    solar_wind_speed: str = ""
    kp_index: str = ""
    bz_value: str = ""
    density: str = ""
    bt_value: str = ""
    last_x_flare: str = ""
    last_geomagnetic_storm: str = ""
    sunspot_number: str = ""


def spaceweather_conditions(page: Page) -> SpaceWeatherResult:
    """Extract current space weather conditions."""
    print("  Checking current conditions...\n")

    # ── Navigate to homepage ──────────────────────────────────────────
    url = "https://www.spaceweatherlive.com/"
    print(f"Loading {url}...")
    checkpoint("Navigate to SpaceWeatherLive")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = SpaceWeatherResult()

    # ── Extract data from page text ───────────────────────────────────
    checkpoint("Extract space weather data")
    body = page.evaluate("document.body.innerText")

    # Solar wind speed
    m = re.search(r'Speed:\s*([\d.]+)\s*km/sec', body)
    if m:
        result.solar_wind_speed = m.group(1) + " km/sec"

    # Kp index
    m = re.search(r'Kp(\d[\+\-]?)\n', body)
    if m:
        result.kp_index = "Kp" + m.group(1)

    # Bz value
    m = re.search(r'Bz:\s*([\-\d.]+)\s*nT\s*(North|South)?', body)
    if m:
        result.bz_value = m.group(1) + " nT" + (" " + m.group(2) if m.group(2) else "")

    # Density
    m = re.search(r'Density:\s*([\d.]+)\s*p/cm3', body)
    if m:
        result.density = m.group(1) + " p/cm3"

    # Bt value
    m = re.search(r'Bt:\s*([\d.]+)\s*nT', body)
    if m:
        result.bt_value = m.group(1) + " nT"

    # Last X-flare
    m = re.search(r'Last X-flare\s+(\S+)\s+(X[\d.]+)', body)
    if m:
        result.last_x_flare = f"{m.group(2)} on {m.group(1)}"

    # Last geomagnetic storm
    m = re.search(r'Last geomagnetic storm\s+(\S+)\s+(Kp\S+)\s*\((\w+)\)', body)
    if m:
        result.last_geomagnetic_storm = f"{m.group(2)} ({m.group(3)}) on {m.group(1)}"

    # Sunspot number
    m = re.search(r'Monthly mean Sunspot Number\n(\w+\s+\d{4})\s+([\d.]+)', body)
    if m:
        result.sunspot_number = f"{m.group(2)} ({m.group(1)})"

    # ── Print results ─────────────────────────────────────────────────
    print(f"  Solar Wind Speed:       {result.solar_wind_speed}")
    print(f"  Kp Index:               {result.kp_index}")
    print(f"  Bz:                     {result.bz_value}")
    print(f"  Density:                {result.density}")
    print(f"  Bt:                     {result.bt_value}")
    print(f"  Last X-Flare:           {result.last_x_flare}")
    print(f"  Last Geomagnetic Storm: {result.last_geomagnetic_storm}")
    print(f"  Sunspot Number:         {result.sunspot_number}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("spaceweather")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = spaceweather_conditions(page)
            print("\n=== DONE ===")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
