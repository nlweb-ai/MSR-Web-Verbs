"""Playwright script (Python) — SimplyHired"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class SimplyHiredRequest:
    query: str = "product manager"
    location: str = "San Francisco, CA"
    max_results: int = 5

@dataclass
class JobItem:
    title: str = ""
    company: str = ""
    location: str = ""
    salary: str = ""

@dataclass
class SimplyHiredResult:
    jobs: List[JobItem] = field(default_factory=list)

def search_simplyhired(page: Page, request: SimplyHiredRequest) -> SimplyHiredResult:
    url = f"https://www.simplyhired.com/search?q={request.query.replace(' ', '+')}&l={request.location.replace(' ', '+')}"
    checkpoint("Navigate to SimplyHired search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    result = SimplyHiredResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find jobs section: line ending with "jobs in <location>"
        let start = 0;
        for (let i = 0; i < lines.length; i++) {
            if (/jobs in /i.test(lines[i])) { start = i + 1; break; }
        }
        // Parse job blocks: Title, Company—Location, optional Salary, ...
        // Company line contains em-dash (\u2014) separating company from location
        const dashRe = /\u2014|\u00a0\u2014/;
        for (let i = start; i < lines.length && results.length < max; i++) {
            // If next line has em-dash → this line is title
            if (i + 1 < lines.length && dashRe.test(lines[i + 1])) {
                const title = lines[i];
                const compLine = lines[i + 1];
                const parts = compLine.split(/\u2014/);
                const company = (parts[0] || '').replace(/\u00a0/g, ' ').trim();
                const locPart = (parts[1] || '').trim();
                // Remove trailing rating number like "4.1"
                const location = locPart.replace(/[\\d.]+$/, '').trim();
                // Check next line for salary
                let salary = '';
                if (i + 2 < lines.length && /^\\$/.test(lines[i + 2])) {
                    salary = lines[i + 2];
                }
                results.push({ title, company, location, salary });
                i += 2;
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = JobItem()
        item.title = d.get("title", "")
        item.company = d.get("company", "")
        item.location = d.get("location", "")
        item.salary = d.get("salary", "")
        result.jobs.append(item)

    print(f"\nFound {len(result.jobs)} jobs:")
    for i, j in enumerate(result.jobs, 1):
        print(f"\n  {i}. {j.title}")
        print(f"     {j.company} - {j.location}  Salary: {j.salary}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("simplyhired")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_simplyhired(page, SimplyHiredRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
