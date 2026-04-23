"""Playwright script (Python) — TheTVDB"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class TVDBRequest:
    show: str = "Breaking Bad"
    max_results: int = 5

@dataclass
class TVDBItem:
    name: str = ""
    year: str = ""
    media_type: str = ""
    description: str = ""

@dataclass
class TVDBResult:
    items: List[TVDBItem] = field(default_factory=list)

def search_tvdb(page: Page, request: TVDBRequest) -> TVDBResult:
    url = f"https://thetvdb.com/search?query={request.show.replace(' ', '+')}"
    checkpoint("Navigate to TheTVDB search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    result = TVDBResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: Name line, then "YEAR, Type #ID" or ", Type #ID", then description
        for (let i = 0; i < lines.length && results.length < max; i++) {
            const m = lines[i].match(/^(\\d{4})?,?\\s*(Series|Movie|List)\\s+#\\d+$/);
            if (m && i >= 1) {
                const name = lines[i - 1];
                const year = m[1] || '';
                const media_type = m[2];
                // Description on next line (skip "Alternate Titles:")
                let description = '';
                if (i + 1 < lines.length && lines[i + 1] !== 'Alternate Titles:') {
                    description = lines[i + 1].substring(0, 200);
                } else if (i + 2 < lines.length && lines[i + 1] === 'Alternate Titles:' && i + 3 < lines.length) {
                    // No description for this item
                }
                if (name && name.length > 2) {
                    results.push({ name, year, media_type, description });
                }
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = TVDBItem()
        item.name = d.get("name", "")
        item.year = d.get("year", "")
        item.media_type = d.get("media_type", "")
        item.description = d.get("description", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} results:")
    for i, it in enumerate(result.items, 1):
        print(f"  {i}. {it.name} ({it.year}) [{it.media_type}] - {it.description[:60]}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("tvdb")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_tvdb(page, TVDBRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
