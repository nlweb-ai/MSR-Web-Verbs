"""
Auto-generated Playwright script (Python)
CourtListener – Court Opinion Search
Query: "freedom of speech"

Generated on: 2026-04-18T05:08:44.857Z
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
class OpinionRequest:
    query: str = "freedom of speech"
    max_results: int = 5


@dataclass
class Opinion:
    case_name: str = ""
    court: str = ""
    date_filed: str = ""
    summary: str = ""


@dataclass
class OpinionResult:
    opinions: list = field(default_factory=list)


def courtlistener_search(page: Page, request: OpinionRequest) -> OpinionResult:
    """Search CourtListener for court opinions."""
    print(f"  Query: {request.query}\n")

    url = f"https://www.courtlistener.com/?q={quote_plus(request.query)}&type=o"
    print(f"Loading {url}...")
    checkpoint("Navigate to CourtListener search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract opinion listings")
    items_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const items = document.querySelectorAll(
            'article, [class*="result"], .search-result, ol > li'
        );
        const seen = new Set();
        for (const item of items) {
            if (results.length >= maxResults) break;
            const titleEl = item.querySelector('a[href*="/opinion/"], h3 a, h4 a, [class*="title"] a');
            const case_name = titleEl ? titleEl.innerText.trim() : '';
            if (!case_name || case_name.length < 3 || seen.has(case_name)) continue;
            seen.add(case_name);

            const text = item.innerText || '';
            let court = '', date_filed = '', summary = '';

            const courtEl = item.querySelector('[class*="court"], [class*="jurisdiction"]');
            if (courtEl) court = courtEl.innerText.trim();

            const dateM = text.match(/(\w+\s+\d{1,2},?\s+\d{4}|\d{4}-\d{2}-\d{2})/);
            if (dateM) date_filed = dateM[1];

            const descEl = item.querySelector('p, [class*="desc"], [class*="snippet"]');
            if (descEl) summary = descEl.innerText.trim().slice(0, 200);

            results.push({ case_name, court, date_filed, summary });
        }
        return results;
    }""", request.max_results)

    result = OpinionResult(opinions=[Opinion(**o) for o in items_data])

    print("\n" + "=" * 60)
    print(f"CourtListener: {request.query}")
    print("=" * 60)
    for o in result.opinions:
        print(f"  {o.case_name}")
        print(f"    Court: {o.court}  Filed: {o.date_filed}")
        print(f"    Summary: {o.summary[:80]}...")
    print(f"\n  Total: {len(result.opinions)} opinions")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("courtlistener_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = courtlistener_search(page, OpinionRequest())
            print(f"\nReturned {len(result.opinions)} opinions")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
