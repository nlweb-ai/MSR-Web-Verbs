"""
RxList – Search for medication information by keyword

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class RxlistSearchRequest:
    search_query: str = "ibuprofen"
    max_results: int = 5


@dataclass
class RxlistDrugItem:
    drug_name: str = ""
    generic_name: str = ""
    drug_class: str = ""
    uses: str = ""
    side_effects: str = ""
    dosage_forms: str = ""


@dataclass
class RxlistSearchResult:
    items: List[RxlistDrugItem] = field(default_factory=list)


# Search for medication information on RxList by keyword.
def rxlist_search(page: Page, request: RxlistSearchRequest) -> RxlistSearchResult:
    """Search for medication information on RxList."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://www.rxlist.com/{request.search_query.replace(' ', '_').lower()}-drug.htm"
    print(f"Loading {url}...")
    checkpoint("Navigate to RxList drug page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = RxlistSearchResult()

    checkpoint("Extract drug listings")
    js_code = """(max) => {
        const links = document.querySelectorAll('a[href]');
        const seen = new Set();
        const items = [];
        for (const a of links) {
            if (items.length >= max) break;
            const href = a.getAttribute('href') || '';
            // Match RxList drug pages
            if (!href.match(/rxlist\\.com\\/[a-z].*-drug\\.htm/)) continue;
            if (seen.has(href)) continue;
            seen.add(href);
            const text = a.textContent.trim();
            if (!text || text.length < 3 || text.length > 200) continue;
            // Skip nav-like links
            if (/^(Drugs|A-Z|Home|Search|Browse)/i.test(text)) continue;
            items.push({drug_name: text, generic_name: '', drug_class: '', uses: '', side_effects: '', dosage_forms: ''});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = RxlistDrugItem()
        item.drug_name = d.get("drug_name", "")
        item.generic_name = d.get("generic_name", "")
        item.drug_class = d.get("drug_class", "")
        item.uses = d.get("uses", "")
        item.side_effects = d.get("side_effects", "")
        item.dosage_forms = d.get("dosage_forms", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Drug {i}:")
        print(f"    Name:         {item.drug_name}")
        print(f"    Generic:      {item.generic_name}")
        print(f"    Class:        {item.drug_class}")
        print(f"    Uses:         {item.uses[:100]}...")
        print(f"    Side Effects: {item.side_effects[:100]}...")
        print(f"    Dosage Forms: {item.dosage_forms}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("rxlist")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = RxlistSearchRequest()
            result = rxlist_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} drugs")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
