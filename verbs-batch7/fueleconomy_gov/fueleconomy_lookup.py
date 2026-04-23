"""
Auto-generated Playwright script (Python)
FuelEconomy.gov – Vehicle fuel economy lookup

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class FuelEconomyRequest:
    year: int = 2025
    make: str = "Toyota"
    model: str = "Camry"


@dataclass
class VehicleTrim:
    trim: str = ""
    fuel_type: str = ""
    city_mpg: int = 0
    highway_mpg: int = 0
    combined_mpg: int = 0


@dataclass
class FuelEconomyResult:
    trims: List[VehicleTrim] = field(default_factory=list)


def fueleconomy_lookup(page: Page, request: FuelEconomyRequest) -> FuelEconomyResult:
    """Look up vehicle fuel economy data."""
    print(f"  Vehicle: {request.year} {request.make} {request.model}\n")

    checkpoint("Navigate to FuelEconomy.gov")
    url = f"https://www.fueleconomy.gov/feg/bymodel/{request.year}_{request.make}_{request.model}.shtml"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract fuel economy data")
    result = FuelEconomyResult()

    items = page.evaluate(r"""() => {
        const rows = document.querySelectorAll('tr');
        const results = [];
        for (let i = 0; i < rows.length; i++) {
            const row = rows[i];
            const mpg = row.querySelector('.mpgSummary');
            if (!mpg) continue;
            
            // MPG values
            const text = mpg.textContent;
            const cityMatch = text.match(/City MPG:\s*(\d+)/);
            const hwyMatch = text.match(/Highway MPG:\s*(\d+)/);
            const combMatch = text.match(/Combined MPG:\s*(\d+)/);
            
            // Walk backwards through sibling rows to find trim name and fuel type
            let trimName = '';
            let fuelType = '';
            let prev = row.previousElementSibling;
            while (prev) {
                const t = prev.textContent.trim().replace(/\s+/g, ' ');
                if (t.match(/Gasoline|Diesel|Electricity|E85|Hydrogen/i) && !fuelType) {
                    fuelType = t.split(/\s{2,}/)[0].replace(/View Estimates.*/, '').replace(/Not Available.*/, '').trim();
                }
                if (t.match(/^\d{4}\s/) && t.includes('cyl,')) {
                    trimName = t;
                    break;
                }
                prev = prev.previousElementSibling;
            }
            
            results.push({
                trim: trimName,
                fuel_type: fuelType,
                city_mpg: cityMatch ? parseInt(cityMatch[1]) : 0,
                highway_mpg: hwyMatch ? parseInt(hwyMatch[1]) : 0,
                combined_mpg: combMatch ? parseInt(combMatch[1]) : 0
            });
        }
        return results;
    }""")

    for item in items:
        t = VehicleTrim()
        t.trim = item.get("trim", "")
        t.fuel_type = item.get("fuel_type", "")
        t.city_mpg = item.get("city_mpg", 0)
        t.highway_mpg = item.get("highway_mpg", 0)
        t.combined_mpg = item.get("combined_mpg", 0)
        result.trims.append(t)

    print(f"  Loading {url}...\n")
    for i, t in enumerate(result.trims):
        print(f"  Trim {i + 1}:")
        print(f"    Name:     {t.trim}")
        print(f"    Fuel:     {t.fuel_type}")
        print(f"    City:     {t.city_mpg} MPG")
        print(f"    Highway:  {t.highway_mpg} MPG")
        print(f"    Combined: {t.combined_mpg} MPG")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("fueleconomy")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = FuelEconomyRequest()
            result = fueleconomy_lookup(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.trims)} trims")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
