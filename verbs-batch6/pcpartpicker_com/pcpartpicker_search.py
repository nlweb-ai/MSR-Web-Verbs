"""
Auto-generated Playwright script (Python)
PCPartPicker – PC Parts Search
Query: "RTX 4070 graphics card"
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
class PartRequest:
    query: str = "RTX 4070 graphics card"
    max_results: int = 5


@dataclass
class Part:
    name: str = ""
    price: str = ""
    url: str = ""


@dataclass
class PartResult:
    parts: List[Part] = field(default_factory=list)


def pcpartpicker_search(page: Page, request: PartRequest) -> PartResult:
    """Search PCPartPicker for PC parts via Google site search."""
    print(f"  Query: {request.query}\n")

    from urllib.parse import quote_plus
    url = f"https://www.google.com/search?q=site%3Apcpartpicker.com+{quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Google site search for PCPartPicker")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    checkpoint("Extract part listings from Google results")
    parts_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();
        const h3s = document.querySelectorAll('h3');
        for (const h of h3s) {
            if (results.length >= maxResults) break;
            let text = h.innerText.trim();
            text = text.replace(/\s*[\|\u2013\u2014-]\s*PCPartPicker.*$/i, '').trim();
            if (text.length < 5 || seen.has(text)) continue;
            seen.add(text);

            let url = '';
            const link = h.closest('a') || h.parentElement?.closest('a');
            if (link) url = link.href || '';

            let price = '';
            const pm = text.match(/(\$[\d,]+(?:\.\d{2})?)/);
            if (pm) price = pm[1];

            results.push({ name: text.slice(0, 150), price, url });
        }
        return results;
    }""", request.max_results)

    parts = [Part(**d) for d in parts_data]
    result = PartResult(parts=parts[:request.max_results])

    print("\n" + "=" * 60)
    print(f"PCPartPicker: {request.query}")
    print("=" * 60)
    for i, p in enumerate(result.parts, 1):
        print(f"  {i}. {p.name}")
        if p.price:
            print(f"     Price: {p.price}")
        if p.url:
            print(f"     URL:   {p.url}")
    print(f"\nTotal: {len(result.parts)} parts")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("pcpartpicker_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = pcpartpicker_search(page, PartRequest())
            print(f"\nReturned {len(result.parts)} parts")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
