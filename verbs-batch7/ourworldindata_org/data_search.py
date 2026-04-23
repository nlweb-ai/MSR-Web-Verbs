"""
Our World in Data – Search

Search OWID for articles/charts and extract the top results:
title, description, and URL.
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
    Query: str = "CO2 emissions by country"
    num_results: int = 5


@dataclass
class SearchResult:
    title: str = ""
    description: str = ""
    url: str = ""


@dataclass
class Result:
    results: List[SearchResult] = field(default_factory=list)


def data_search(page, request: Request) -> Result:
    """Search Our World in Data and extract top results."""

    url = f"https://ourworldindata.org/search?q={quote(request.Query)}"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    data = page.evaluate(r"""(numResults) => {
        const headers = document.querySelectorAll('a.search-chart-hit-header');
        return Array.from(headers).slice(0, numResults).map(a => {
            const fullText = a.textContent.trim();
            // Title is before "Source:", description is the source line
            const parts = fullText.split('Source:');
            const title = parts[0].trim();
            const description = parts.length > 1
                ? parts.slice(1).join('Source:').split('Source:')[0].trim()
                : '';
            return {
                title,
                description: description ? 'Source: ' + description : '',
                url: a.href,
            };
        });
    }""", request.num_results)

    return Result(
        results=[
            SearchResult(
                title=r.get("title", ""),
                description=r.get("description", ""),
                url=r.get("url", ""),
            )
            for r in data
        ]
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("owid_search")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            req = Request(Query="CO2 emissions by country", num_results=5)
            result = data_search(page, req)
            print(f"\nSearch Results ({len(result.results)}):")
            for i, r in enumerate(result.results, 1):
                print(f"\n  {i}. {r.title}")
                print(f"     {r.description}")
                print(f"     {r.url}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
