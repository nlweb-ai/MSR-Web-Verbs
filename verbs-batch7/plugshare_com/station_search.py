"""
PlugShare – EV Charging Station Search

Search PlugShare directory for EV charging stations and extract
station name, address, checkins, and detail URL.
"""

import os, sys, re, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws


@dataclass(frozen=True)
class Request:
    City: str = "San Francisco"
    State: str = "California"
    num_results: int = 5


@dataclass
class Station:
    name: str = ""
    address: str = ""
    checkins: str = ""
    url: str = ""


@dataclass
class Result:
    total_stations: str = ""
    stations: List[Station] = field(default_factory=list)


def station_search(page, request: Request) -> Result:
    """Search PlugShare directory for EV charging stations."""

    city_slug = request.City.lower().replace(" ", "-")
    state_slug = request.State.lower().replace(" ", "-")
    url = f"https://www.plugshare.com/directory/us/{state_slug}/{city_slug}"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    data = page.evaluate(r"""(numResults) => {
        // Get total station count
        const countEl = document.querySelector('.station-count');
        const totalStations = countEl ? countEl.textContent.trim() : '';

        // Get station cards
        const locations = document.querySelectorAll('div.location');
        const stations = Array.from(locations).slice(0, numResults).map(loc => {
            const text = loc.innerText.trim();
            const lines = text.split('\n').map(l => l.trim()).filter(l => l);

            // First line: "Station Name (X checkins)"
            const nameMatch = lines[0]?.match(/^(.+?)\s*\((\d+)\s*checkins?\)/);
            const name = nameMatch ? nameMatch[1].trim() : lines[0] || '';
            const checkins = nameMatch ? nameMatch[2] : '';

            // Second line: address
            const address = lines[1] || '';

            // Get detail link
            const link = loc.querySelector('a[href*="/location/"]');
            const detailUrl = link ? link.href : '';

            return { name, address, checkins, url: detailUrl };
        });

        return { totalStations, stations };
    }""", request.num_results)

    return Result(
        total_stations=data.get("totalStations", ""),
        stations=[
            Station(
                name=s.get("name", ""),
                address=s.get("address", ""),
                checkins=s.get("checkins", ""),
                url=s.get("url", ""),
            )
            for s in data.get("stations", [])
        ],
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("plugshare_search")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            req = Request(City="San Francisco", State="California", num_results=5)
            result = station_search(page, req)
            print(f"\nTotal Stations: {result.total_stations}")
            print(f"\nTop {len(result.stations)} Charging Stations:")
            for i, s in enumerate(result.stations, 1):
                print(f"\n  {i}. {s.name} ({s.checkins} checkins)")
                print(f"     {s.address}")
                print(f"     {s.url}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
