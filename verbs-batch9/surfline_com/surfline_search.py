"""
Surfline – Search for surf forecasts by keyword

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
class SurflineSearchRequest:
    search_query: str = "Malibu"
    max_results: int = 5


@dataclass
class SurflineSpotItem:
    spot_name: str = ""
    location: str = ""


@dataclass
class SurflineSearchResult:
    items: List[SurflineSpotItem] = field(default_factory=list)


# Search for surf forecasts on Surfline by keyword.
def surfline_search(page: Page, request: SurflineSearchRequest) -> SurflineSearchResult:
    """Search for surf forecasts on Surfline."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://www.surfline.com/search/{query}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Surfline search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = SurflineSearchResult()

    checkpoint("Extract surf spot listings")
    js_code = """(max) => {
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        const results = [];
        let inSpots = false;
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'Surf Spots') { inSpots = true; continue; }
            if (inSpots && (lines[i] === 'Map Area' || lines[i] === 'Surf News' || lines[i] === 'Travel Guide')) break;
            if (inSpots) {
                // Name and location are concatenated: "NameCountry / Region"
                const m = lines[i].match(/^(.+?[a-z])([A-Z].+\\s\\/\\s.+)$/);
                if (m) {
                    results.push({ spot_name: m[1], location: m[2] });
                }
            }
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = SurflineSpotItem()
        item.spot_name = d.get("spot_name", "")
        item.location = d.get("location", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} spots:")
    for i, item in enumerate(result.items, 1):
        print(f"  {i}. {item.spot_name} - {item.location}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("surfline")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SurflineSearchRequest()
            result = surfline_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} spots")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
