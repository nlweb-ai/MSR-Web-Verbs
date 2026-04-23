"""
Playwright script (Python) — Minted Wedding Invitations Search
Search Minted for wedding invitation designs.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MintedRequest:
    query: str = "modern minimalist wedding invitations"
    max_results: int = 5


@dataclass
class DesignItem:
    name: str = ""
    artist: str = ""


@dataclass
class MintedResult:
    designs: List[DesignItem] = field(default_factory=list)


# Searches Minted for wedding invitation designs and extracts
# design name, artist, price, and number of color options.
def search_minted(page: Page, request: MintedRequest) -> MintedResult:
    url = f"https://www.minted.com/wedding-invitations?search={request.query.replace(' ', '+')}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Minted search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = MintedResult()

    checkpoint("Extract design listings")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        // Minted uses DIV containers with store links inside
        const storeLinks = document.querySelectorAll('a[href*="/store/"]');
        for (const a of storeLinks) {
            if (results.length >= max) break;
            // Walk up to find the product container (css-y4zyec)
            let container = a;
            for (let j = 0; j < 4; j++) { if (container.parentElement) container = container.parentElement; }
            const text = container.innerText.trim();
            const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            const name = lines[0] || '';
            if (!name || name.length < 2 || seen.has(name)) continue;
            seen.add(name);

            const artistLine = lines.find(l => l.startsWith('By '));
            const artist = artistLine ? artistLine.replace(/^By\\s+/, '') : '';

            const priceLine = lines.find(l => l.match(/^\\$/));
            const price = priceLine || '';

            const colorMatch = text.match(/(\\d+)\\s*color/i);
            const color_options = colorMatch ? colorMatch[1] : '';

            results.push({ name, artist, price, color_options });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = DesignItem()
        item.name = d.get("name", "")
        item.artist = d.get("artist", "")
        result.designs.append(item)

    print(f"\nFound {len(result.designs)} designs:")
    for i, d in enumerate(result.designs, 1):
        print(f"\n  {i}. {d.name}")
        print(f"     Artist: {d.artist}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("minted")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_minted(page, MintedRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.designs)} designs")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
