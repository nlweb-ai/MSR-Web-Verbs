"""
Auto-generated Playwright script (Python)
numbeo.com – Cost of Living Comparison
Compare "New York, NY" vs "London"

Generated on: 2026-04-18T01:49:38.165Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class NumbeoRequest:
    city1: str = "New York, NY"
    country1: str = "United States"
    city2: str = "London"
    country2: str = "United Kingdom"


@dataclass(frozen=True)
class IndexComparison:
    category: str = ""
    difference: str = ""


@dataclass(frozen=True)
class CityIndex:
    city: str = ""
    cost_of_living_index: str = ""


@dataclass(frozen=True)
class NumbeoResult:
    indices: list = None       # list[IndexComparison]
    city_indices: list = None  # list[CityIndex]


def numbeo_compare(page: Page, request: NumbeoRequest) -> NumbeoResult:
    """Compare cost of living between two cities on Numbeo."""
    print(f"  Comparing: {request.city1} vs {request.city2}\n")

    # ── Navigate to comparison page ───────────────────────────────────
    url = (
        "https://www.numbeo.com/cost-of-living/compare_cities.jsp"
        f"?country1={quote(request.country1)}&city1={quote(request.city1)}"
        f"&country2={quote(request.country2)}&city2={quote(request.city2)}"
    )
    print(f"Loading {url}...")
    checkpoint("Navigate to Numbeo comparison page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Extract indices differences (Table 1) ─────────────────────────
    indices = page.evaluate(r"""() => {
        const table = document.querySelector('table.table_indices_diff');
        if (!table) return [];
        const rows = table.querySelectorAll('tr');
        const results = [];
        for (const row of rows) {
            const text = row.innerText.trim();
            if (!text) continue;
            // Parse: "Category in City2 is X% lower/higher than in City1"
            const match = text.match(/^(.+?)\s+in\s+.+?\s+(?:is|are)\s+([\d.]+%\s+(?:lower|higher))\s+than\s+in\s+/);
            if (match) {
                results.push({ category: match[1].trim(), difference: match[2].trim() });
            }
        }
        return results;
    }""")

    # ── Extract city index values (Table 3) ───────────────────────────
    city_indices = page.evaluate(r"""(cities) => {
        const tables = document.querySelectorAll('table');
        for (const table of tables) {
            const text = table.innerText;
            if (text.includes('Cost of Living Index') && !text.includes('lower') && !text.includes('higher')) {
                const rows = table.querySelectorAll('tr');
                const results = [];
                for (const row of rows) {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 2) {
                        const city = cells[0].innerText.trim();
                        const index = cells[1].innerText.trim();
                        if (cities.some(c => city.toLowerCase().includes(c.toLowerCase()))) {
                            results.push({ city, cost_of_living_index: index });
                        }
                    }
                }
                if (results.length > 0) return results;
            }
        }
        return [];
    }""", [request.city1, request.city2])

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Cost of Living Comparison: {request.city1} vs {request.city2}")
    print("=" * 60)

    print("\n  Summary Indices:")
    for idx in indices:
        print(f"    {idx['category']}: {idx['difference']}")

    if city_indices:
        print("\n  Cost of Living Index:")
        for ci in city_indices:
            print(f"    {ci['city']}: {ci['cost_of_living_index']}")

    return NumbeoResult(
        indices=[IndexComparison(**i) for i in indices],
        city_indices=[CityIndex(**ci) for ci in city_indices],
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("numbeo_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = numbeo_compare(page, NumbeoRequest())
            print(f"\nReturned {len(result.indices or [])} indices, {len(result.city_indices or [])} city indices")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
