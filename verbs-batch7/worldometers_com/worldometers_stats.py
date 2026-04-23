"""
Auto-generated Playwright script (Python)
Worldometers – Real-time World Statistics

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class StatsRequest:
    pass


@dataclass
class StatsResult:
    world_population: str = ""
    births_today: str = ""
    deaths_today: str = ""
    net_growth_today: str = ""
    births_this_year: str = ""
    deaths_this_year: str = ""
    net_growth_this_year: str = ""


def worldometers_stats(page: Page, request: StatsRequest) -> StatsResult:
    """Extract real-time world population statistics from Worldometers."""
    print("  Loading Worldometers...\n")

    url = "https://www.worldometers.info"
    checkpoint("Navigate to Worldometers")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = StatsResult()

    checkpoint("Extract statistics")
    js_code = r"""() => {
        const lines = document.body.innerText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        const data = {};
        for (let i = 0; i < lines.length; i++) {
            const label = lines[i].toLowerCase();
            if (label === 'current world population' && i > 0) data.world_population = lines[i-1];
            else if (label === 'births today' && i > 0) data.births_today = lines[i-1];
            else if (label === 'deaths today' && i > 0) data.deaths_today = lines[i-1];
            else if (label === 'net population growth today' && i > 0) data.net_growth_today = lines[i-1];
            else if (label === 'births this year' && i > 0) data.births_this_year = lines[i-1];
            else if (label === 'deaths this year' && i > 0) data.deaths_this_year = lines[i-1];
            else if (label === 'net population growth this year' && i > 0) data.net_growth_this_year = lines[i-1];
        }
        return data;
    }"""
    data = page.evaluate(js_code)

    result.world_population = data.get("world_population", "")
    result.births_today = data.get("births_today", "")
    result.deaths_today = data.get("deaths_today", "")
    result.net_growth_today = data.get("net_growth_today", "")
    result.births_this_year = data.get("births_this_year", "")
    result.deaths_this_year = data.get("deaths_this_year", "")
    result.net_growth_this_year = data.get("net_growth_this_year", "")

    print(f"  World Population:       {result.world_population}")
    print(f"  Births Today:           {result.births_today}")
    print(f"  Deaths Today:           {result.deaths_today}")
    print(f"  Net Growth Today:       {result.net_growth_today}")
    print(f"  Births This Year:       {result.births_this_year}")
    print(f"  Deaths This Year:       {result.deaths_this_year}")
    print(f"  Net Growth This Year:   {result.net_growth_this_year}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("worldometers")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = StatsRequest()
            result = worldometers_stats(page, request)
            print("\n=== DONE ===")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
