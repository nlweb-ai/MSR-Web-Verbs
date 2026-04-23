"""Playwright script (Python) — SSA.gov"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class SSARequest:
    topic: str = "retirement benefits"

@dataclass
class ResourceSection:
    title: str = ""
    description: str = ""

@dataclass
class SSAResult:
    topic: str = ""
    summary: str = ""
    sections: List[ResourceSection] = field(default_factory=list)

def get_ssa_info(page: Page, request: SSARequest) -> SSAResult:
    url = "https://www.ssa.gov/benefits/retirement/"
    checkpoint("Navigate to SSA retirement page")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    result = SSAResult()
    result.topic = "Retirement Benefits"
    js_code = """() => {
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        let summary = '';
        const sections = [];
        // Find "Retirement benefits" header, next line is summary
        const markers = ['Learn how to apply', 'Learn about retirement planning', 'See when to apply', 'See how to report'];
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === 'Retirement benefits' && i + 1 < lines.length) {
                summary = lines[i + 1];
            }
            // Sections: title line followed by description, then a CTA marker
            if (markers.some(m => lines[i].startsWith(m)) && i >= 2) {
                sections.push({ title: lines[i - 2], description: lines[i - 1] });
            }
        }
        return { summary, sections };
    }"""
    data = page.evaluate(js_code)
    result.summary = data.get("summary", "")
    for s in data.get("sections", []):
        sec = ResourceSection()
        sec.title = s.get("title", "")
        sec.description = s.get("description", "")
        result.sections.append(sec)

    print(f"\nFound {len(result.sections)} sections:")
    print(f"  Summary: {result.summary[:80]}")
    for i, s in enumerate(result.sections, 1):
        print(f"  {i}. {s.title}: {s.description[:80]}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("ssa")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            get_ssa_info(page, SSARequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
