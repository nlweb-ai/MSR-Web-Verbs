"""Playwright script (Python) — TVmaze"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class TVMazeRequest:
    show: str = "The Office"
    max_results: int = 5

@dataclass
class TVMazeItem:
    name: str = ""
    network: str = ""
    years: str = ""
    last_episode: str = ""

@dataclass
class TVMazeResult:
    items: List[TVMazeItem] = field(default_factory=list)

def search_tvmaze(page: Page, request: TVMazeRequest) -> TVMazeResult:
    url = f"https://www.tvmaze.com/search?q={request.show.replace(' ', '+')}"
    checkpoint("Navigate to TVmaze search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)
    result = TVMazeResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: "ShowName (Network , YYYY - YYYY)" then "Previous episode: Title"
        for (let i = 0; i < lines.length && results.length < max; i++) {
            const m = lines[i].match(/^(.+?)\\s*\\((.+?)\\s*,\\s*(\\d{4}\\s*-\\s*(?:\\d{4}|now))\\)$/);
            if (m) {
                const name = m[1].trim();
                const network = m[2].trim();
                const years = m[3].trim();
                let last_episode = '';
                if (i + 1 < lines.length && lines[i + 1].startsWith('Previous episode:')) {
                    last_episode = lines[i + 1].replace('Previous episode: ', '');
                }
                results.push({ name, network, years, last_episode });
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = TVMazeItem()
        item.name = d.get("name", "")
        item.network = d.get("network", "")
        item.years = d.get("years", "")
        item.last_episode = d.get("last_episode", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} shows:")
    for i, s in enumerate(result.items, 1):
        print(f"  {i}. {s.name} ({s.network}, {s.years}) - Last: {s.last_episode}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("tvmaze")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_tvmaze(page, TVMazeRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
