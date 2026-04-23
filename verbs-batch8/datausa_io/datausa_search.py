"""
Auto-generated Playwright script (Python)
DataUSA – Look up demographic/economic data for a US location
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class DatausaSearchRequest:
    search_query: str = "Chicago"
    max_results: int = 5


@dataclass
class DatausaLocationItem:
    location_name: str = ""
    population: str = ""
    median_income: str = ""
    poverty_rate: str = ""
    median_age: str = ""
    employment_rate: str = ""


@dataclass
class DatausaSearchResult:
    items: List[DatausaLocationItem] = field(default_factory=list)


# Look up demographic and economic data for a US location on DataUSA.
def datausa_search(page: Page, request: DatausaSearchRequest) -> DatausaSearchResult:
    """Look up demographic/economic data for a US location on DataUSA."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://datausa.io/search?q={query}"
    print(f"Loading {url}...")
    checkpoint("Navigate to DataUSA search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = DatausaSearchResult()

    checkpoint("Extract location data listings")
    js_code = """(max) => {
        const cards = document.querySelectorAll('[class*="SearchResult"], [class*="result"], [class*="Card"], [class*="card"], [class*="profile"], article, li[class*="item"]');
        const items = [];
        for (const card of cards) {
            if (items.length >= max) break;
            const nameEl = card.querySelector('h2, h3, h4, [class*="title"], [class*="name"] a, a[class*="link"]');
            const popEl = card.querySelector('[class*="population"], [class*="pop"]');
            const incomeEl = card.querySelector('[class*="income"], [class*="median"]');
            const povertyEl = card.querySelector('[class*="poverty"]');
            const ageEl = card.querySelector('[class*="age"]');
            const employEl = card.querySelector('[class*="employ"], [class*="employment"]');

            const location_name = nameEl ? nameEl.textContent.trim() : '';
            const population = popEl ? popEl.textContent.trim() : '';
            const median_income = incomeEl ? incomeEl.textContent.trim() : '';
            const poverty_rate = povertyEl ? povertyEl.textContent.trim() : '';
            const median_age = ageEl ? ageEl.textContent.trim() : '';
            const employment_rate = employEl ? employEl.textContent.trim() : '';

            if (location_name) {
                items.push({location_name, population, median_income, poverty_rate, median_age, employment_rate});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = DatausaLocationItem()
        item.location_name = d.get("location_name", "")
        item.population = d.get("population", "")
        item.median_income = d.get("median_income", "")
        item.poverty_rate = d.get("poverty_rate", "")
        item.median_age = d.get("median_age", "")
        item.employment_rate = d.get("employment_rate", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Location {i}:")
        print(f"    Name:       {item.location_name}")
        print(f"    Population: {item.population}")
        print(f"    Income:     {item.median_income}")
        print(f"    Poverty:    {item.poverty_rate}")
        print(f"    Med. Age:   {item.median_age}")
        print(f"    Employment: {item.employment_rate}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("datausa")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = DatausaSearchRequest()
            result = datausa_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} locations")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
