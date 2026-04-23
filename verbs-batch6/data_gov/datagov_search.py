"""
Auto-generated Playwright script (Python)
Data.gov – Government Dataset Search
Query: "air quality"

Generated on: 2026-04-18T05:09:58.280Z
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
class DatasetRequest:
    query: str = "air quality"
    max_results: int = 5


@dataclass
class Dataset:
    title: str = ""
    publisher: str = ""
    description: str = ""
    url: str = ""


@dataclass
class DatasetResult:
    datasets: list = field(default_factory=list)


def datagov_search(page: Page, request: DatasetRequest) -> DatasetResult:
    """Search Data.gov catalog for government datasets."""
    print(f"  Query: {request.query}\n")

    # ── Step 1: Navigate to Data.gov and search ───────────────────────
    print("Loading https://catalog.data.gov ...")
    checkpoint("Navigate to Data.gov catalog")
    page.goto("https://catalog.data.gov/", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Type into search input
    search = page.locator('input[type="search"], input[name="q"], input[placeholder*="Search" i]').first
    search.click()
    page.wait_for_timeout(300)
    search.fill(request.query)
    page.wait_for_timeout(300)
    search.press("Enter")
    page.wait_for_timeout(5000)

    # ── Step 2: Extract dataset results ───────────────────────────────
    checkpoint("Extract dataset listings")
    items_data = page.evaluate(r"""(maxResults) => {
        const items = document.querySelectorAll('.organization-datasets__item, li[class*="dataset"]');
        const results = [];
        for (const item of items) {
            if (results.length >= maxResults) break;

            // Title from h3 a or heading link
            const titleEl = item.querySelector('h3 a, h2 a, [class*="heading"] a');
            const title = titleEl ? titleEl.innerText.trim() : '';
            if (!title) continue;
            const url = titleEl ? titleEl.href : '';

            // Organization - parse from full text
            const fullText = item.innerText;
            let publisher = '';
            const orgMatch = fullText.match(/Organization:\s*(.+?)(?:\n|Updated)/);
            if (orgMatch) publisher = orgMatch[1].trim();

            // Description
            const descEl = item.querySelector('p');
            const description = descEl ? descEl.innerText.trim() : '';

            results.push({ title, publisher, description, url });
        }
        return results;
    }""", request.max_results)

    result = DatasetResult(datasets=[Dataset(**d) for d in items_data])

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Data.gov: {request.query}")
    print("=" * 60)
    for i, d in enumerate(items_data, 1):
        print(f"\n  {i}. {d['title']}")
        print(f"     Publisher: {d['publisher']}")
        print(f"     Description: {d['description'][:150]}...")
        print(f"     URL: {d['url']}")
    print(f"\n  Total: {len(result.datasets)} datasets")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("data_gov")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = datagov_search(page, DatasetRequest())
            print(f"\nReturned {len(result.datasets)} datasets")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
