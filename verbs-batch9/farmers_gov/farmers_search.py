"""
Playwright script (Python) — Farmers.gov USDA Resource Search
Search for USDA resources on Farmers.gov.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class FarmersGovSearchRequest:
    search_query: str = "crop insurance"
    max_results: int = 5


@dataclass
class ResourceItem:
    title: str = ""
    description: str = ""
    link: str = ""


@dataclass
class FarmersGovSearchResult:
    query: str = ""
    items: List[ResourceItem] = field(default_factory=list)


# Searches Farmers.gov for USDA resources matching the query and returns
# up to max_results resources with title, description, and link.
def search_farmers_gov(page: Page, request: FarmersGovSearchRequest) -> FarmersGovSearchResult:
    import urllib.parse
    url = f"https://www.farmers.gov/search?query={urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = FarmersGovSearchResult(query=request.search_query)

    checkpoint("Extract resource listings")
    js_code = """(max) => {
        const results = [];
        const cards = document.querySelectorAll('.search-result, article, [class*="result"], [class*="views-row"], li[class*="item"]');
        for (const card of cards) {
            if (results.length >= max) break;
            const titleEl = card.querySelector('h2, h3, h4, a[class*="title"], [class*="field-title"]');
            const title = titleEl ? titleEl.textContent.trim() : '';
            if (!title || title.length < 5) continue;
            if (results.some(r => r.title === title)) continue;

            let category = '';
            const catEl = card.querySelector('[class*="type"], [class*="category"], [class*="tag"], span[class*="label"]');
            if (catEl) category = catEl.textContent.trim();

            let description = '';
            const descEl = card.querySelector('p, [class*="description"], [class*="summary"], [class*="snippet"]');
            if (descEl) description = descEl.textContent.trim().substring(0, 200);

            let link = '';
            const linkEl = card.querySelector('a[href]');
            if (linkEl) {
                link = linkEl.href || linkEl.getAttribute('href') || '';
                if (link.startsWith('/')) link = 'https://www.farmers.gov' + link;
            }

            results.push({ title, category, description, link });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ResourceItem()
        item.title = d.get("title", "")
        item.description = d.get("description", "")
        item.link = d.get("link", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} resources for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Description: {item.description[:100]}...")
        print(f"     Link: {item.link}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("farmers_gov")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_farmers_gov(page, FarmersGovSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} resources")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
