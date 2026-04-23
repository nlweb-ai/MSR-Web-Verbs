"""
Auto-generated Playwright script (Python)
Library of Congress – Digital Collections Search
Query: "civil war photographs"

Generated on: 2026-04-18T14:48:01.971Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class LocRequest:
    query: str = "civil war photographs"
    max_results: int = 5


@dataclass
class LocItem:
    title: str = ""
    creator: str = ""
    date: str = ""
    collection: str = ""
    url: str = ""


@dataclass
class LocResult:
    items: List[LocItem] = field(default_factory=list)


def loc_search(page: Page, request: LocRequest) -> LocResult:
    """Search Library of Congress digital collections."""
    print(f"  Query: {request.query}\n")

    # LOC is behind Cloudflare, use Google site search
    from urllib.parse import quote_plus
    url = f"https://www.google.com/search?q=site%3Aloc.gov+{quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Google site search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract search results")
    items_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();

        // Get Google result headings (h3) paired with their cite elements
        const h3s = document.querySelectorAll('h3');
        for (const h of h3s) {
            if (results.length >= maxResults) break;
            let title = h.innerText.trim();
            title = title.replace(/\s*[\|–—-]\s*Library of Congress.*$/i, '').trim();
            title = title.replace(/\s*[\|–—-]\s*loc\.gov.*$/i, '').trim();
            if (!title || title.length < 5 || seen.has(title)) continue;
            if (/^(search|sign|log|menu|home|all|images|videos|news|more|tools)/i.test(title)) continue;
            seen.add(title);

            // Get parent container for URL and snippet
            const container = h.closest('[data-snhf]') || h.closest('[class*="g"]') || h.parentElement?.parentElement;
            let itemUrl = '', creator = '', date = '', collection = '';
            if (container) {
                const a = container.querySelector('a');
                if (a) itemUrl = a.getAttribute('href') || '';
                const text = container.innerText || '';
                const dateM = text.match(/(\d{4})/);
                if (dateM) date = dateM[1];
                const byM = text.match(/by\s+([A-Z][^,\n]{2,40})/);
                if (byM) creator = byM[1].trim();
                if (/collection|division|prints|photographs/i.test(text)) {
                    const cm = text.match(/((?:Prints|Photographs|Manuscript|Rare Book|Music|Geography)[^\n.]{5,60})/i);
                    if (cm) collection = cm[1].trim();
                }
            }

            results.push({
                title: title.slice(0, 120),
                creator: creator.slice(0, 60),
                date,
                collection: collection.slice(0, 80),
                url: itemUrl
            });
        }
        return results;
    }""", request.max_results)

    items = [LocItem(**d) for d in items_data]

    result = LocResult(items=items[:request.max_results])

    print("\n" + "=" * 60)
    print(f"Library of Congress: {request.query}")
    print("=" * 60)
    for i, item in enumerate(result.items, 1):
        print(f"  {i}. {item.title}")
        if item.creator:
            print(f"     Creator:    {item.creator}")
        if item.date:
            print(f"     Date:       {item.date}")
        if item.collection:
            print(f"     Collection: {item.collection}")
        if item.url:
            print(f"     URL:        {item.url}")
    print(f"\nTotal: {len(result.items)} items")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("loc_gov")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = loc_search(page, LocRequest())
            print(f"\nReturned {len(result.items)} items")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
