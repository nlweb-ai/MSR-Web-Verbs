"""
Auto-generated Playwright script (Python)
Formula 1 – Driver standings

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class StandingsRequest:
    max_results: int = 10


@dataclass
class Driver:
    position: int = 0
    driver_name: str = ""
    nationality: str = ""
    team: str = ""
    points: int = 0


@dataclass
class StandingsResult:
    drivers: List[Driver] = field(default_factory=list)


def f1_standings(page: Page, request: StandingsRequest) -> StandingsResult:
    """Extract F1 driver standings."""
    print("  Loading F1 driver standings...\n")

    checkpoint("Navigate to F1 standings")
    page.goto("https://www.formula1.com/en/results/2025/drivers", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract standings table")
    result = StandingsResult()

    drivers_data = page.evaluate(
        r"""(max) => {
            const rows = document.querySelectorAll('table tbody tr');
            const items = [];
            for (let i = 0; i < rows.length && items.length < max; i++) {
                const cells = rows[i].querySelectorAll('td');
                if (cells.length < 5) continue;
                
                const pos = parseInt(cells[0].textContent.trim()) || 0;
                // Driver cell may have name + abbreviation concatenated
                const driverText = cells[1].textContent.trim();
                // Remove trailing 3-letter abbreviation (e.g., "Lando NorrisNOR" -> "Lando Norris")
                const driver = driverText.replace(/([a-z])([A-Z]{3})$/, '$1');
                const nationality = cells[2].textContent.trim();
                const team = cells[3].textContent.trim();
                const pts = parseInt(cells[4].textContent.trim()) || 0;
                
                items.push({position: pos, driver_name: driver, nationality, team, points: pts});
            }
            return items;
        }""",
        request.max_results,
    )

    for d in drivers_data:
        driver = Driver()
        driver.position = d.get("position", 0)
        driver.driver_name = d.get("driver_name", "")
        driver.nationality = d.get("nationality", "")
        driver.team = d.get("team", "")
        driver.points = d.get("points", 0)
        result.drivers.append(driver)

    for d in result.drivers:
        print(f"  {d.position:>2}. {d.driver_name:<25} {d.team:<20} {d.nationality:<5} {d.points} pts")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("f1")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = StandingsRequest()
            result = f1_standings(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.drivers)} drivers")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
