"""
Auto-generated Playwright script (Python)
cdc.gov – Health Information Search
Query: flu vaccination

Generated on: 2026-04-18T00:31:02.749Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from playwright.sync_api import Playwright, sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CDCSearchRequest:
    search_query: str = "flu vaccination"
    max_results: int = 5


@dataclass(frozen=True)
class CDCResult:
    page_title: str = ""
    summary: str = ""
    url: str = ""


@dataclass(frozen=True)
class CDCSearchResult:
    results: list = None  # list[CDCResult]


def cdc_search(page: Page, request: CDCSearchRequest) -> CDCSearchResult:
    """Search CDC.gov for health information."""
    query = request.search_query
    max_results = request.max_results
    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    # ── Navigate to search results page ───────────────────────────────
    import urllib.parse
    url = f"https://search.cdc.gov/search/index.html?query={urllib.parse.quote_plus(query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to CDC search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    # ── Extract results ───────────────────────────────────────────────
    checkpoint("Extract search results")
    results_data = page.evaluate(r"""(maxResults) => {
        const items = document.querySelectorAll('div.result');
        const results = [];
        for (const item of items) {
            if (results.length >= maxResults) break;
            const titleEl = item.querySelector('.result-title a');
            const descEl = item.querySelector('.result-description');
            if (!titleEl) continue;

            const pageTitle = (titleEl.textContent || '').trim();
            const url = titleEl.href || '';
            let summary = (descEl ? descEl.textContent : '').trim();
            // Remove "View in Page" suffix
            summary = summary.replace(/\s*View in Page\s*$/, '').trim();

            if (pageTitle) {
                results.push({ pageTitle, summary, url });
            }
        }
        return results;
    }""", max_results)

    results = []
    for r in results_data:
        results.append(CDCResult(
            page_title=r.get("pageTitle", ""),
            summary=r.get("summary", ""),
            url=r.get("url", ""),
        ))

    # ── Print results ─────────────────────────────────────────────────
    print("=" * 60)
    print(f'CDC.gov - "{query}" Search Results')
    print("=" * 60)
    for idx, r in enumerate(results, 1):
        print(f"\n{idx}. {r.page_title}")
        print(f"   URL: {r.url}")
        print(f"   Summary: {r.summary[:150]}")

    print(f"\nFound {len(results)} results")
    return CDCSearchResult(results=results)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("cdc_gov")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = cdc_search(page, CDCSearchRequest())
            print(f"\nReturned {len(result.results or [])} results")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
