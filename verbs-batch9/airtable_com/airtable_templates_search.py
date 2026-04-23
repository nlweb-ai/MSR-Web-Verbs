"""
Playwright script (Python) — Airtable Template Search
Search for Airtable templates and extract details.
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
class AirtableTemplateSearchRequest:
    search_query: str = "content calendar"
    max_results: int = 5


@dataclass
class TemplateItem:
    template_name: str = ""


@dataclass
class AirtableTemplateSearchResult:
    query: str = ""
    items: List[TemplateItem] = field(default_factory=list)


# Searches Airtable templates and extracts template names.
def search_airtable_templates(page: Page, request: AirtableTemplateSearchRequest) -> AirtableTemplateSearchResult:
    """Search Airtable templates."""
    encoded = quote_plus(request.search_query)
    url = f"https://www.airtable.com/templates?query={encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Airtable templates")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = AirtableTemplateSearchResult(query=request.search_query)

    checkpoint("Extract templates")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();
        const h3s = document.querySelectorAll('h3');
        for (const h3 of h3s) {
            if (items.length >= max) break;
            const name = h3.innerText.trim();
            if (!name || name.length < 5 || seen.has(name)) continue;
            if (name.match(/^(Sign|Log|Menu|Filter|Sort|Privacy|Cookie)/i)) continue;
            seen.add(name);
            items.push({template_name: name});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = TemplateItem()
        item.template_name = d.get("template_name", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} templates for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.template_name}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("airtable")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_airtable_templates(page, AirtableTemplateSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} templates")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
