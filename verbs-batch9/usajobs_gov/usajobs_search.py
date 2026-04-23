"""Playwright script (Python) — USAJobs"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class USAJobsRequest:
    query: str = "information technology"
    location: str = "Washington, DC"
    max_results: int = 5

@dataclass
class JobItem:
    title: str = ""
    department: str = ""
    location: str = ""
    salary: str = ""
    closing: str = ""

@dataclass
class USAJobsResult:
    jobs: List[JobItem] = field(default_factory=list)

def search_usajobs(page: Page, request: USAJobsRequest) -> USAJobsResult:
    url = f"https://www.usajobs.gov/Search/Results?k={request.query.replace(' ', '+')}"
    checkpoint("Navigate to USAJobs search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = USAJobsResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: Title → "Save job" → sub-agency → Department → Location → Office → salary → type → dates
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'Save job' && i >= 1 && i + 6 < lines.length) {
                const title = lines[i - 1];
                if (!title || title.length < 5) continue;
                // Lines after "Save job": sub-agency, department, location, office, salary, type, dates
                let department = '', location = '', salary = '', closing = '';
                for (let j = i + 1; j < Math.min(i + 8, lines.length); j++) {
                    if (lines[j].startsWith('Department of ') || lines[j].startsWith('Department Of ')) {
                        department = lines[j];
                    }
                    if (lines[j].startsWith('Starting at ')) {
                        salary = lines[j];
                    }
                    if (/^Open \\d/.test(lines[j])) {
                        closing = lines[j];
                    }
                    if (!location && j === i + 3) {
                        location = lines[j];
                    }
                }
                results.push({ title, department, location, salary, closing });
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = JobItem()
        item.title = d.get("title", "")
        item.department = d.get("department", "")
        item.location = d.get("location", "")
        item.salary = d.get("salary", "")
        item.closing = d.get("closing", "")
        result.jobs.append(item)

    print(f"\nFound {len(result.jobs)} jobs:")
    for i, j in enumerate(result.jobs, 1):
        print(f"  {i}. {j.title} - {j.department} - {j.salary}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("usajobs")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_usajobs(page, USAJobsRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
