"""
Playwright script (Python) — Find a Grave Memorial Search
Search for memorials on FindAGrave.com.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class FindAGraveSearchRequest:
    last_name: str = "Roosevelt"
    location: str = "New York"
    max_results: int = 5


@dataclass
class MemorialItem:
    full_name: str = ""
    birth_date: str = ""
    death_date: str = ""
    cemetery: str = ""
    location: str = ""


@dataclass
class FindAGraveSearchResult:
    last_name: str = ""
    location: str = ""
    items: List[MemorialItem] = field(default_factory=list)


# Searches FindAGrave.com for memorials matching the last name and location,
# returning up to max_results with full name, birth/death dates, cemetery, and location.
def search_findagrave(page: Page, request: FindAGraveSearchRequest) -> FindAGraveSearchResult:
    import urllib.parse
    url = f"https://www.findagrave.com/memorial/search?lastname={urllib.parse.quote_plus(request.last_name)}&location={urllib.parse.quote_plus(request.location)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = FindAGraveSearchResult(last_name=request.last_name, location=request.location)

    checkpoint("Extract memorial listings")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        const items = document.querySelectorAll('div.memorial-item');
        for (const item of items) {
            if (results.length >= max) break;
            const lines = item.innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 3) continue;
            // Filter out status lines like "No grave photo", "Flowers have been left."
            const filtered = lines.filter(l => {
                const t = l.trim();
                return t !== 'No grave photo' && t !== 'Flowers have been left.' && !t.startsWith('Plot info:');
            });
            if (filtered.length < 3) continue;
            const name = filtered[0].trim();
            if (!name || name.length < 2 || seen.has(name + filtered[1])) continue;
            seen.add(name + filtered[1]);
            const dates = filtered[1] ? filtered[1].trim() : '';
            const cemetery = filtered[2] ? filtered[2].trim() : '';
            const location = filtered[3] ? filtered[3].trim() : '';
            // Parse born/died from dates like "2 Feb 1907 \u2013 17 Jun 1945" or "1902 \u2013 unknown"
            let born = '', died = '';
            const parts = dates.split('\u2013');
            if (parts.length === 2) {
                born = parts[0].trim();
                died = parts[1].trim();
            } else {
                born = dates;
            }
            results.push({full_name: name, birth_date: born, death_date: died, cemetery, location});
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = MemorialItem()
        item.full_name = d.get("full_name", "")
        item.birth_date = d.get("birth_date", "")
        item.death_date = d.get("death_date", "")
        item.cemetery = d.get("cemetery", "")
        item.location = d.get("location", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} memorials for '{request.last_name}' in '{request.location}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.full_name}")
        print(f"     Born: {item.birth_date}  Died: {item.death_date}")
        print(f"     Cemetery: {item.cemetery}  Location: {item.location}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("findagrave")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_findagrave(page, FindAGraveSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} memorials")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
