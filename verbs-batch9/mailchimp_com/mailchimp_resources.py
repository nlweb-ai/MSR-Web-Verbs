"""
Playwright script (Python) — Mailchimp Resources
Browse Mailchimp resources and extract articles/guides.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MailchimpRequest:
    search_query: str = "audience segmentation"
    max_results: int = 5


@dataclass
class ResourceItem:
    title: str = ""
    type: str = ""
    summary: str = ""


@dataclass
class MailchimpResult:
    query: str = ""
    resources: List[ResourceItem] = field(default_factory=list)


# Browses Mailchimp resources page and extracts resource titles,
# types (guide, article, tutorial), and summaries.
def search_mailchimp_resources(page: Page, request: MailchimpRequest) -> MailchimpResult:
    url = "https://mailchimp.com/resources/"
    print(f"Loading {url}...")
    checkpoint("Navigate to Mailchimp resources")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = MailchimpResult(query=request.search_query)

    checkpoint("Extract resource listings")
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        const cats = ['Articles', 'Case Study', 'Reports & Downloads'];
        const seen = new Set();
        for (let i = 1; i < lines.length && results.length < max; i++) {
            if (cats.includes(lines[i])) {
                const title = lines[i - 1];
                const type = lines[i];
                const summary = (i + 1 < lines.length && !cats.includes(lines[i + 1])) ? lines[i + 1] : '';
                if (title && title.length > 5 && !seen.has(title)) {
                    seen.add(title);
                    results.push({ title, type, summary });
                }
            }
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ResourceItem()
        item.title = d.get("title", "")
        item.type = d.get("type", "")
        item.summary = d.get("summary", "")
        result.resources.append(item)

    print(f"\nFound {len(result.resources)} resources:")
    for i, item in enumerate(result.resources, 1):
        print(f"\n  {i}. [{item.type}] {item.title}")
        print(f"     Summary: {item.summary[:80]}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("mailchimp")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_mailchimp_resources(page, MailchimpRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.resources)} resources")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
