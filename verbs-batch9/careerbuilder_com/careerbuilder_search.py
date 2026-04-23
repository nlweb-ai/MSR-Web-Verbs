"""
Playwright script (Python) — CareerBuilder Job Search
Search for jobs on CareerBuilder.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CareerBuilderSearchRequest:
    query: str = "marketing manager"
    location: str = "New York, NY"
    max_results: int = 5


@dataclass
class JobItem:
    title: str = ""
    company: str = ""
    location: str = ""
    salary_range: str = ""
    employment_type: str = ""


@dataclass
class CareerBuilderSearchResult:
    query: str = ""
    location: str = ""
    items: List[JobItem] = field(default_factory=list)


def search_careerbuilder(page: Page, request: CareerBuilderSearchRequest) -> CareerBuilderSearchResult:
    """Search CareerBuilder for jobs."""
    url = "https://www.careerbuilder.com/"
    print(f"Loading {url}...")
    checkpoint("Navigate to CareerBuilder")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Fill search form and submit")
    page.fill('input[name="q"]', request.query)
    page.fill('input[name="where"]', request.location)
    page.keyboard.press("Enter")
    page.wait_for_timeout(8000)

    result = CareerBuilderSearchResult(query=request.query, location=request.location)

    checkpoint("Extract job listings")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('[class*="job"], [class*="listing"], [class*="card"], [data-job-id], li[class*="data-results"]');
        for (const card of cards) {
            if (items.length >= max) break;
            const text = (card.textContent || '').replace(/\\s+/g, ' ').trim();

            let title = '';
            const titleEl = card.querySelector('[class*="title"] a, h2 a, h3 a, [class*="job-title"]');
            if (titleEl) title = titleEl.textContent.trim();
            if (!title || title.length < 3 || title.length > 200) continue;
            if (items.some(i => i.title === title)) continue;

            let company = '';
            const compEl = card.querySelector('[class*="company"], [class*="employer"]');
            if (compEl) company = compEl.textContent.trim();

            let location = '';
            const locEl = card.querySelector('[class*="location"]');
            if (locEl) location = locEl.textContent.trim();

            let salary = '';
            const salMatch = text.match(/\\$[\\d,]+(?:\\s*-\\s*\\$[\\d,]+)?(?:\\s*(?:\\/|per)\\s*(?:year|yr|hour|hr))?/i);
            if (salMatch) salary = salMatch[0];

            let empType = '';
            const typeMatch = text.match(/(full[- ]?time|part[- ]?time|contract|temporary|remote)/i);
            if (typeMatch) empType = typeMatch[1];

            items.push({title: title, company: company, location: location, salary_range: salary, employment_type: empType});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = JobItem()
        item.title = d.get("title", "")
        item.company = d.get("company", "")
        item.location = d.get("location", "")
        item.salary_range = d.get("salary_range", "")
        item.employment_type = d.get("employment_type", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} jobs for '{request.query}' in '{request.location}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Company: {item.company}  Location: {item.location}")
        print(f"     Salary: {item.salary_range}  Type: {item.employment_type}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("careerbuilder")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_careerbuilder(page, CareerBuilderSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} jobs")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
