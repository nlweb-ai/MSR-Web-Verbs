"""
Playwright script (Python) — Crates.io Search
Search for Rust crates on crates.io.
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
class CratesSearchRequest:
    query: str = "async runtime"
    max_results: int = 5


@dataclass
class CrateItem:
    name: str = ""
    version: str = ""
    downloads: str = ""
    description: str = ""
    last_updated: str = ""


@dataclass
class CratesSearchResult:
    query: str = ""
    items: List[CrateItem] = field(default_factory=list)


def search_crates(page: Page, request: CratesSearchRequest) -> CratesSearchResult:
    """Search crates.io for Rust crates."""
    encoded = quote_plus(request.query)
    url = f"https://crates.io/search?q={encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = CratesSearchResult(query=request.query)

    checkpoint("Extract crates")
    js_code = """(max) => {
        const items = [];
        const links = document.querySelectorAll('a[href^="/crates/"]');
        const seen = new Set();
        for (const link of links) {
            if (items.length >= max) break;
            const name = link.textContent.trim();
            if (!name || seen.has(name)) continue;
            seen.add(name);

            // Get the parent list item
            const li = link.closest('li');
            if (!li) continue;
            const lines = li.innerText.split('\\n').map(l => l.trim()).filter(l => l);

            let version = '';
            let description = '';
            let allTimeDownloads = '';
            let recentDownloads = '';
            let updated = '';
            for (const line of lines) {
                if (line.startsWith('v') && /^v\\d+/.test(line)) { version = line; continue; }
                if (line.startsWith('All-Time:')) { allTimeDownloads = line.replace('All-Time: ', ''); continue; }
                if (line.startsWith('Recent:')) { recentDownloads = line.replace('Recent: ', ''); continue; }
                if (line.startsWith('Updated:')) { updated = line.replace('Updated: ', ''); continue; }
                if (['Homepage', 'Documentation', 'Repository'].includes(line)) continue;
                if (line === name) continue;
                if (!description && line.length > 10) description = line;
            }

            items.push({name, version, description, downloads: allTimeDownloads, last_updated: updated});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = CrateItem()
        item.name = d.get("name", "")
        item.version = d.get("version", "")
        item.downloads = d.get("downloads", "")
        item.description = d.get("description", "")
        item.last_updated = d.get("last_updated", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} crates for '{request.query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name} {item.version}")
        print(f"     Downloads: {item.downloads}  Updated: {item.last_updated}")
        print(f"     {item.description[:100]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("crates")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_crates(page, CratesSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} crates")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
