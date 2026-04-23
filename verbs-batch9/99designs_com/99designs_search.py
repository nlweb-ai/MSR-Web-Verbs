"""
Playwright script (Python) — 99designs Designer Search
Search for designers by category and extract their profiles.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class DesignSearchRequest:
    category: str = "website design"
    max_results: int = 5


@dataclass
class DesignerItem:
    designer_name: str = ""


@dataclass
class DesignSearchResult:
    category: str = ""
    items: List[DesignerItem] = field(default_factory=list)


# Searches 99designs for designers in a given design category and extracts
# designer names.
def search_99designs(page: Page, request: DesignSearchRequest) -> DesignSearchResult:
    """Search 99designs for designers by category."""
    print(f"  Category: {request.category}\n")

    url = "https://99designs.com/designers"
    print(f"Loading {url}...")
    checkpoint("Navigate to 99designs designers page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Dismiss cookie banner if present
    for sel in ['button:has-text("Accept")', 'button:has-text("Got it")', '[aria-label="Close"]']:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.evaluate("el => el.click()")
                page.wait_for_timeout(500)
        except Exception:
            pass

    result = DesignSearchResult(category=request.category)

    # Scroll to load more content
    for _ in range(3):
        page.evaluate("window.scrollBy(0, 600)")
        page.wait_for_timeout(800)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(500)

    checkpoint("Extract designer listings")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();
        // Get all profile links and their surrounding context
        const profileLinks = document.querySelectorAll('a[href*="/profiles/"]');
        for (const link of profileLinks) {
            if (items.length >= max) break;
            const name = link.textContent.trim();
            if (!name || name.length < 2 || name.length > 100) continue;
            if (/^(find|become|browse|sign|log|search|view|see|all|by\\s)/i.test(name)) continue;
            const key = name.toLowerCase();
            if (seen.has(key)) continue;
            seen.add(key);

            // Get context from parent container
            const parent = link.closest('div, li, article, section') || link.parentElement;

            items.push({designer_name: name});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = DesignerItem()
        item.designer_name = d.get("designer_name", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} designers for '{request.category}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.designer_name}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("99designs")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = DesignSearchRequest()
            result = search_99designs(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} designers")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
