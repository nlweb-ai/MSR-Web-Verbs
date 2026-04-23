"""
Playwright script (Python) — GAO Report Search
Search for GAO reports on gao.gov.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GAOSearchRequest:
    search_query: str = "cybersecurity"
    max_results: int = 5


@dataclass
class ReportItem:
    title: str = ""
    report_number: str = ""
    publish_date: str = ""
    summary: str = ""


@dataclass
class GAOSearchResult:
    query: str = ""
    items: List[ReportItem] = field(default_factory=list)


# Searches GAO.gov for government reports matching the query and returns
# up to max_results reports with title, report number, publish date, and summary.
def search_gao_reports(page: Page, request: GAOSearchRequest) -> GAOSearchResult:
    import urllib.parse
    url = f"https://www.gao.gov/search?keyword={urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = GAOSearchResult(query=request.search_query)

    checkpoint("Extract report listings")
    js_code = """(max) => {
        const results = [];
        const cards = document.querySelectorAll('[class*="search-result"], article, [class*="result"], [class*="views-row"], li[class*="item"]');
        for (const card of cards) {
            if (results.length >= max) break;
            const titleEl = card.querySelector('h2, h3, h4, a[class*="title"], [class*="report-title"]');
            const title = titleEl ? titleEl.textContent.trim() : '';
            if (!title || title.length < 10) continue;
            if (results.some(r => r.title === title)) continue;

            const text = (card.textContent || '').replace(/\\s+/g, ' ').trim();

            let reportNumber = '';
            const numMatch = text.match(/(GAO-\\d{2}-\\d+[A-Z]*)/i);
            if (numMatch) reportNumber = numMatch[1];

            let publishDate = '';
            const dateEl = card.querySelector('time, [class*="date"], [datetime]');
            if (dateEl) publishDate = (dateEl.getAttribute('datetime') || dateEl.textContent || '').trim();
            if (!publishDate) {
                const dateMatch = text.match(/(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\w*\\s+\\d{1,2},?\\s+\\d{4}/i);
                if (dateMatch) publishDate = dateMatch[0];
            }

            let summary = '';
            const descEl = card.querySelector('p, [class*="summary"], [class*="description"], [class*="snippet"]');
            if (descEl) summary = descEl.textContent.trim().substring(0, 200);

            results.push({ title, report_number: reportNumber, publish_date: publishDate, summary });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ReportItem()
        item.title = d.get("title", "")
        item.report_number = d.get("report_number", "")
        item.publish_date = d.get("publish_date", "")
        item.summary = d.get("summary", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} reports for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Report #: {item.report_number}  Date: {item.publish_date}")
        print(f"     Summary: {item.summary[:100]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("gao")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_gao_reports(page, GAOSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} reports")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
