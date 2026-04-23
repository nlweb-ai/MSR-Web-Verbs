"""
Can I Use – Search browser compatibility data

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
import urllib.parse
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CaniuseSearchRequest:
    feature_query: str = "flexbox"


@dataclass
class CaniuseFeatureItem:
    feature_name: str = ""
    description: str = ""
    usage_percentage: str = ""


@dataclass
class CaniuseSearchResult:
    items: List[CaniuseFeatureItem] = field(default_factory=list)


# Search browser compatibility data on Can I Use.
def caniuse_search(page: Page, request: CaniuseSearchRequest) -> CaniuseSearchResult:
    """Search browser compatibility data on Can I Use."""
    print(f"  Feature query: {request.feature_query}\n")

    encoded = urllib.parse.quote_plus(request.feature_query)
    url = f"https://caniuse.com/?search={encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Can I Use search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = CaniuseSearchResult()

    checkpoint("Extract browser compatibility data")
    js_code = """() => {
        const items = [];
        const ciuList = document.querySelector('ciu-feature-list');
        if (!ciuList || !ciuList.shadowRoot) return items;
        const wrap = ciuList.shadowRoot.querySelector('.feature-list-wrap');
        if (!wrap) return items;
        const features = wrap.querySelectorAll('ciu-feature');
        for (const f of features) {
            const sr = f.shadowRoot;
            if (!sr) continue;
            const titleEl = sr.querySelector('h3.title');
            const descEl = sr.querySelector('p.description');
            const usageEl = sr.querySelector('ciu-feature-usage');
            let name = titleEl ? titleEl.textContent.trim() : '';
            let desc = descEl ? descEl.textContent.trim() : '';
            let usage = '';
            if (usageEl && usageEl.shadowRoot) {
                const uText = usageEl.shadowRoot.textContent || '';
                const um = uText.match(/(\\d+\\.\\d+)%/);
                if (um) usage = um[1] + '%';
            }
            if (name) items.push({feature_name: name, description: desc, usage_percentage: usage});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code)

    for d in items_data:
        item = CaniuseFeatureItem()
        item.feature_name = d.get("feature_name", "")
        item.description = d.get("description", "")
        item.usage_percentage = d.get("usage_percentage", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Feature {i}:")
        print(f"    Name:        {item.feature_name}")
        print(f"    Description: {item.description[:80]}")
        print(f"    Usage:       {item.usage_percentage}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("caniuse")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = CaniuseSearchRequest()
            result = caniuse_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} features")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
