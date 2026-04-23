"""
Auto-generated Playwright script (Python)
Idealist – Non-Profit Job Search
Query: "environmental policy"
Location: "Washington, DC"

Generated on: 2026-04-18T14:42:16.791Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class JobRequest:
    query: str = "environmental policy"
    location: str = "Washington, DC"
    max_results: int = 5


@dataclass
class Job:
    title: str = ""
    organization: str = ""
    location: str = ""
    job_type: str = ""


@dataclass
class JobResult:
    jobs: List[Job] = field(default_factory=list)


def idealist_search(page: Page, request: JobRequest) -> JobResult:
    """Search Idealist for non-profit jobs."""
    print(f"  Query: {request.query}")
    print(f"  Location: {request.location}\n")

    # ── Step 1: Navigate to Idealist job search ───────────────────────
    from urllib.parse import quote_plus
    url = f"https://www.idealist.org/en/jobs?q={quote_plus(request.query)}&searchLocation={quote_plus(request.location + ', USA')}"
    print("Loading Idealist search...")
    checkpoint("Navigate to Idealist search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Step 2: Parse job listings from body text ─────────────────────
    checkpoint("Extract job listings")
    items = page.evaluate(r"""(maxResults) => {
        const text = document.body.innerText;
        const results = [];
        const jobTypes = ['Full Time', 'Part Time', 'Contract/Freelance', 'Volunteer', 'Temporary', 'Internship'];
        const locTypes = ['Hybrid', 'Remote', 'On-site'];

        // Split by "Posted X ago" markers to get blocks
        const blocks = text.split(/Posted \d+ (?:days?|hours?|minutes?|months?) ago/);

        for (const block of blocks) {
            if (results.length >= maxResults) break;
            const lines = block.trim().split('\n').map(l => l.trim()).filter(Boolean);
            if (lines.length < 4) continue;

            // Find job type line
            let jobTypeIdx = -1;
            let jobType = '';
            for (let i = 0; i < lines.length; i++) {
                for (const jt of jobTypes) {
                    if (lines[i] === jt) { jobTypeIdx = i; jobType = jt; break; }
                }
                if (jobTypeIdx >= 0) break;
            }
            if (jobTypeIdx < 0) continue;

            // Find location type before job type
            let locTypeIdx = -1;
            for (let i = jobTypeIdx - 1; i >= 0; i--) {
                for (const lt of locTypes) {
                    if (lines[i] === lt) { locTypeIdx = i; break; }
                }
                if (locTypeIdx >= 0) break;
            }
            if (locTypeIdx < 2) continue;

            const title = lines[locTypeIdx - 2] || '';
            const org = lines[locTypeIdx - 1] || '';
            const location = lines[locTypeIdx + 1] || '';

            // Skip ads/promos
            if (title.includes('Salary Explorer') || title.includes('Take Our') ||
                title.length < 3 || org.length < 2) continue;

            results.push({ title, org, location, jobType });
        }
        return results;
    }""", request.max_results)

    result = JobResult(jobs=[Job(
        title=j['title'], organization=j['org'],
        location=j['location'], job_type=j['jobType']
    ) for j in items])

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Idealist: \"{request.query}\" near {request.location}")
    print("=" * 60)
    for i, j in enumerate(items, 1):
        print(f"\n  {i}. {j['title']}")
        print(f"     Org: {j['org']}")
        print(f"     Location: {j['location']}  |  Type: {j['jobType']}")
    print(f"\n  Total: {len(items)} jobs")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("idealist_org")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = idealist_search(page, JobRequest())
            print(f"\nReturned {len(result.jobs)} jobs")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
