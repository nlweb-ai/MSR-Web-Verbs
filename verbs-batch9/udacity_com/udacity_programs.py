"""Playwright script (Python) — Udacity"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class UdacityRequest:
    topic: str = "artificial intelligence"
    max_results: int = 5

@dataclass
class ProgramItem:
    name: str = ""
    program_type: str = ""
    rating: str = ""
    level: str = ""
    duration: str = ""

@dataclass
class UdacityResult:
    programs: List[ProgramItem] = field(default_factory=list)

def search_udacity(page: Page, request: UdacityRequest) -> UdacityResult:
    url = "https://www.udacity.com/catalog"
    checkpoint("Navigate to Udacity catalog")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    result = UdacityResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: Name, Description, Type (NANODEGREE PROGRAM/COURSE), Rating, Level, Hours
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'NANODEGREE PROGRAM' || lines[i] === 'COURSE') {
                const program_type = lines[i];
                const name = i >= 2 ? lines[i - 2] : '';
                const rating = (i + 1 < lines.length) ? lines[i + 1] : '';
                const level = (i + 2 < lines.length) ? lines[i + 2] : '';
                const duration = (i + 3 < lines.length) ? lines[i + 3] : '';
                if (name && name.length > 3) {
                    results.push({ name, program_type, rating, level, duration });
                }
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = ProgramItem()
        item.name = d.get("name", "")
        item.program_type = d.get("program_type", "")
        item.rating = d.get("rating", "")
        item.level = d.get("level", "")
        item.duration = d.get("duration", "")
        result.programs.append(item)

    print(f"\nFound {len(result.programs)} programs:")
    for i, p in enumerate(result.programs, 1):
        print(f"  {i}. {p.name} ({p.program_type}) - {p.rating} - {p.level} - {p.duration}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("udacity")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_udacity(page, UdacityRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
