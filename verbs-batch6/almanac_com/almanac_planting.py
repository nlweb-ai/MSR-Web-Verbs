"""
Auto-generated Playwright script (Python)
Almanac – Planting Guide
Plant: "tomatoes"

Generated on: 2026-04-18T04:45:43.384Z
Recorded 4 browser interactions
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
class PlantRequest:
    plant: str = "tomatoes"


@dataclass
class PlantResult:
    plant_name: str = ""
    planting_season: str = ""
    sun_requirements: str = ""
    soil_requirements: str = ""
    days_to_maturity: str = ""
    spacing: str = ""


def almanac_planting(page: Page, request: PlantRequest) -> PlantResult:
    """Look up planting guide on The Old Farmer's Almanac."""
    print(f"  Plant: {request.plant}\n")

    # ── Navigate to Almanac plant page ────────────────────────────────
    url = f"https://www.almanac.com/plant/{quote_plus(request.plant)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Almanac planting guide")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Extract planting info ─────────────────────────────────────────
    checkpoint("Extract planting details")
    data = page.evaluate(r"""() => {
        const text = document.body.innerText;

        // Plant name from h1
        const h1 = document.querySelector('h1');
        const plant_name = h1 ? h1.innerText.trim() : '';

        // Sun exposure (from the info box)
        const sunMatch = text.match(/Sun Exposure\s*\n\s*([^\n]+)/);
        const sun = sunMatch ? sunMatch[1].trim() : '';

        // Soil pH / requirements
        const soilMatch = text.match(/Soil pH\s*\n\s*([^\n]+)/);
        const soil = soilMatch ? soilMatch[1].trim() : '';

        // Planting season
        const seasonMatch = text.match(/When to Plant[^\n]*\n\n([^\n]+)/);
        const planting_season = seasonMatch ? seasonMatch[1].trim().slice(0, 300) : '';

        // Days to maturity
        const daysMatch = text.match(/(\d+\s*days?\s*to\s*(?:more than\s*)?\d+\s*days?)\s*to\s*harvest/i);
        const days = daysMatch ? daysMatch[1] : '';

        // Spacing
        const spacingMatch = text.match(/(?:Plant|space)\s+(?:seedlings?\s+)?(\d+\s*(?:to|[-\u2013])\s*\d+\s*(?:feet|inches|foot)\s*apart)/i);
        const spacing = spacingMatch ? spacingMatch[0] : '';

        return { plant_name, planting_season, sun, soil, days, spacing };
    }""")

    result = PlantResult(
        plant_name=data.get("plant_name", request.plant.title()),
        planting_season=data.get("planting_season", ""),
        sun_requirements=data.get("sun", ""),
        soil_requirements=data.get("soil", ""),
        days_to_maturity=data.get("days", ""),
        spacing=data.get("spacing", ""),
    )

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Almanac: {result.plant_name}")
    print("=" * 60)
    print(f"  Planting Season: {result.planting_season}")
    print(f"  Sun Requirements: {result.sun_requirements}")
    print(f"  Soil Requirements: {result.soil_requirements}")
    print(f"  Days to Maturity: {result.days_to_maturity}")
    print(f"  Spacing: {result.spacing}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("almanac_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = almanac_planting(page, PlantRequest())
            print(f"\nReturned info for {result.plant_name}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
