"""
Auto-generated Playwright script (Python)
Census.gov – Data Search
Query: "population New York"

Generated on: 2026-04-18T05:01:56.313Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CensusRequest:
    query: str = "population New York"
    max_tables: int = 5


@dataclass
class CensusTable:
    title: str = ""
    geographic_area: str = ""
    year: str = ""
    population: str = ""


@dataclass
class CensusResult:
    tables: list = field(default_factory=list)


def census_search(page: Page, request: CensusRequest) -> CensusResult:
    """Search Census.gov for demographic data."""
    print(f"  Query: {request.query}\n")

    url = f"https://data.census.gov/all?q={quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Census data search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    checkpoint("Extract data tables")
    tables_data = page.evaluate(r"""(maxTables) => {
        const results = [];
        const items = document.querySelectorAll(
            '[class*="result"], [class*="table"], article, .search-result, a[href*="/table/"]'
        );
        const seen = new Set();
        for (const item of items) {
            if (results.length >= maxTables) break;
            const titleEl = item.querySelector('h2, h3, h4, [class*="title"], a');
            const title = titleEl ? titleEl.innerText.trim() : '';
            if (!title || title.length < 5 || seen.has(title)) continue;
            seen.add(title);

            const text = item.innerText || '';
            let geographic_area = '', year = '', population = '';

            const yearM = text.match(/(20\d{2}|201\d|202\d)/);
            if (yearM) year = yearM[1];

            const popM = text.match(/(\d[\d,]+)\s*(?:people|population|residents)?/i);
            if (popM) population = popM[1];

            const geoM = text.match(/(?:New York|United States|County|State)/i);
            if (geoM) geographic_area = geoM[0];

            results.push({ title, geographic_area, year, population });
        }
        return results;
    }""", request.max_tables)

    result = CensusResult(tables=[CensusTable(**t) for t in tables_data])

    print("\n" + "=" * 60)
    print(f"Census.gov: {request.query}")
    print("=" * 60)
    for t in result.tables:
        print(f"  {t.title}")
        print(f"    Area: {t.geographic_area}  Year: {t.year}  Population: {t.population}")
    print(f"\n  Total: {len(result.tables)} tables")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("census_gov")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = census_search(page, CensusRequest())
            print(f"\nReturned {len(result.tables)} tables")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
