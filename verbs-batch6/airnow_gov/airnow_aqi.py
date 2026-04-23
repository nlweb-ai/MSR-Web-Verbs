"""
Auto-generated Playwright script (Python)
AirNow – Air Quality Index Lookup
Zip Code: "90210"

Generated on: 2026-04-18T04:36:33.721Z
Recorded 2 browser interactions

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
class AQIRequest:
    zip_code: str = "90210"


@dataclass
class AQIResult:
    location: str = ""
    aqi_value: str = ""
    aqi_category: str = ""
    primary_pollutant: str = ""
    health_recommendation: str = ""


def airnow_aqi(page: Page, request: AQIRequest) -> AQIResult:
    """Look up AQI on AirNow.gov."""
    print(f"  Zip Code: {request.zip_code}\n")

    # ── Navigate to AirNow and enter zip code ──────────────────────────
    url = "https://www.airnow.gov/"
    print(f"Loading {url}...")
    checkpoint("Navigate to AirNow.gov")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Enter zip code in search ─────────────────────────────────────
    checkpoint("Enter zip code")
    search_input = page.locator("#location-input-nav_input").first
    search_input.click()
    page.wait_for_timeout(500)
    search_input.press("Control+a")
    search_input.fill(request.zip_code)
    page.wait_for_timeout(2000)
    search_input.press("Enter")
    page.wait_for_timeout(8000)

    # ── Extract AQI data ─────────────────────────────────────────────
    checkpoint("Extract AQI data")
    data = page.evaluate(r"""() => {
        const result = {};

        // Location - from the curr-cond-label link
        const locEl = document.querySelector('.curr-cond-label a');
        result.location = locEl ? locEl.innerText.trim() : '';

        // AQI value - from the current-aq-data section
        const aqiEl = document.querySelector('.current-aq-data .aqi');
        result.aqi_value = aqiEl ? aqiEl.innerText.trim() : '';

        // AQI category - from the orb class name
        result.aqi_category = '';
        const orbEl = document.querySelector('.aqi-orb');
        if (orbEl) {
            const cls = orbEl.className || '';
            if (cls.includes('hazardous')) result.aqi_category = 'Hazardous';
            else if (cls.includes('very-unhealthy')) result.aqi_category = 'Very Unhealthy';
            else if (cls.includes('usg')) result.aqi_category = 'Unhealthy for Sensitive Groups';
            else if (cls.includes('unhealthy')) result.aqi_category = 'Unhealthy';
            else if (cls.includes('moderate')) result.aqi_category = 'Moderate';
            else if (cls.includes('good')) result.aqi_category = 'Good';
        }

        // Primary pollutant
        const pollEl = document.querySelector('.current-aq-data .pollutant, .aq-dial .pollutant');
        result.primary_pollutant = pollEl
            ? pollEl.innerText.replace(/Pollutant:\s*/i, '').trim()
            : '';

        // Health recommendation - from the forecast pollutant cards
        result.health_recommendation = '';
        const body = document.body?.innerText || '';
        const match = body.match(/If you are.*?outdoors\./s);
        if (match) {
            result.health_recommendation = match[0].replace(/\s+/g, ' ').trim();
        }

        return result;
    }""")

    result = AQIResult(
        location=data.get("location", ""),
        aqi_value=data.get("aqi_value", ""),
        aqi_category=data.get("aqi_category", ""),
        primary_pollutant=data.get("primary_pollutant", ""),
        health_recommendation=data.get("health_recommendation", ""),
    )

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"AirNow AQI: {request.zip_code}")
    print("=" * 60)
    print(f"  Location: {result.location}")
    print(f"  AQI Value: {result.aqi_value}")
    print(f"  Category: {result.aqi_category}")
    print(f"  Primary Pollutant: {result.primary_pollutant}")
    print(f"  Health Recommendation: {result.health_recommendation}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("airnow_gov")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = airnow_aqi(page, AQIRequest())
            print(f"\nDone. AQI: {result.aqi_value} ({result.aqi_category})")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
