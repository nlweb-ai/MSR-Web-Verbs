"""Playwright script (Python) — RubyGems Search"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class RubyGemsRequest:
    query: str = "authentication"
    max_results: int = 5

@dataclass
class GemItem:
    name: str = ""
    version: str = ""
    downloads: str = ""
    description: str = ""

@dataclass
class RubyGemsResult:
    gems: List[GemItem] = field(default_factory=list)

def search_rubygems(page: Page, request: RubyGemsRequest) -> RubyGemsResult:
    url = f"https://rubygems.org/search?query={request.query.replace(' ', '+')}"
    checkpoint("Navigate to RubyGems search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    result = RubyGemsResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find "DISPLAYING GEMS" marker
        let start = 0;
        for (let i = 0; i < lines.length; i++) {
            if (/^DISPLAYING GEMS/i.test(lines[i])) { start = i + 1; break; }
        }
        // Skip FILTER line
        if (start < lines.length && /^FILTER:/i.test(lines[start])) start++;
        // Parse gem blocks: "name version", description, downloads, "DOWNLOADS"
        for (let i = start; i + 3 < lines.length && results.length < max; i++) {
            if (lines[i + 3] === 'DOWNLOADS') {
                const parts = lines[i].split(' ');
                const version = parts.pop() || '';
                const name = parts.join(' ');
                const description = lines[i + 1];
                const downloads = lines[i + 2];
                results.push({ name, version, downloads, description });
                i += 3;
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = GemItem()
        item.name = d.get("name", "")
        item.version = d.get("version", "")
        item.downloads = d.get("downloads", "")
        item.description = d.get("description", "")
        result.gems.append(item)

    print(f"\nFound {len(result.gems)} gems:")
    for i, g in enumerate(result.gems, 1):
        print(f"\n  {i}. {g.name} v{g.version}")
        print(f"     {g.description}")
        print(f"     Downloads: {g.downloads}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("rubygems")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_rubygems(page, RubyGemsRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
