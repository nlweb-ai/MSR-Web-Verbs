"""
Podchaser – Podcast Search

Search Podchaser for podcasts and extract the top results:
podcast name, description, and categories.
"""

import os, sys, shutil
from urllib.parse import quote
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws


@dataclass(frozen=True)
class Request:
    Query: str = "true crime"
    num_results: int = 5


@dataclass
class Podcast:
    name: str = ""
    description: str = ""
    categories: str = ""


@dataclass
class Result:
    total_results: str = ""
    podcasts: List[Podcast] = field(default_factory=list)


def podcast_search(page, request: Request) -> Result:
    """Search Podchaser for podcasts."""

    url = f"https://www.podchaser.com/search/podcasts?q={quote(request.Query)}"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    data = page.evaluate(r"""(numResults) => {
        // Get total result count
        const bodyText = document.body.innerText;
        const countMatch = bodyText.match(/([\d,]+)\s*results/);
        const totalResults = countMatch ? countMatch[1] : '';

        // Get table rows
        const rows = Array.from(document.querySelectorAll('table tbody tr, [role="row"]'));
        const podcasts = rows.slice(0, numResults).map(row => {
            const cells = Array.from(row.cells || row.querySelectorAll('td'));
            return {
                name: cells[1]?.textContent.trim() || '',
                description: cells[2]?.textContent.trim() || '',
                categories: cells[3]?.textContent.trim() || '',
            };
        });

        return { totalResults, podcasts };
    }""", request.num_results)

    return Result(
        total_results=data.get("totalResults", ""),
        podcasts=[
            Podcast(
                name=p.get("name", ""),
                description=p.get("description", ""),
                categories=p.get("categories", ""),
            )
            for p in data.get("podcasts", [])
        ],
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("podchaser_search")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            req = Request(Query="true crime", num_results=5)
            result = podcast_search(page, req)
            print(f"\nTotal Results: {result.total_results}")
            print(f"\nTop {len(result.podcasts)} Podcasts:")
            for i, p in enumerate(result.podcasts, 1):
                print(f"\n  {i}. {p.name}")
                print(f"     Categories: {p.categories}")
                print(f"     {p.description[:150]}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
