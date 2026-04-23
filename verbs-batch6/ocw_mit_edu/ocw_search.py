"""
Auto-generated Playwright script (Python)
MIT OCW – Course Search
Query: "machine learning"
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
class CourseRequest:
    query: str = "machine learning"
    max_results: int = 5


@dataclass
class Course:
    title: str = ""
    number: str = ""
    instructor: str = ""
    url: str = ""


@dataclass
class CourseResult:
    courses: List[Course] = field(default_factory=list)


def ocw_search(page: Page, request: CourseRequest) -> CourseResult:
    """Search MIT OCW for courses."""
    print(f"  Query: {request.query}\n")

    from urllib.parse import quote_plus
    url = f"https://ocw.mit.edu/search/?q={quote_plus(request.query)}&t=course"
    print(f"Loading {url}...")
    checkpoint("Navigate to MIT OCW search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract course listings")
    courses_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();

        // Try course cards or search result items
        const links = document.querySelectorAll('a[href*="/courses/"]');
        for (const a of links) {
            if (results.length >= maxResults) break;
            const href = a.getAttribute('href') || '';
            if (!/\/courses\/[a-z0-9]/.test(href)) continue;

            const text = a.innerText.trim();
            const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 1);
            if (lines.length < 1) continue;

            let title = lines[0];
            if (!title || title.length < 5 || seen.has(title)) continue;
            if (/^(search|home|sign|menu|filter|sort|about|\+\s*\d+\s*more)/i.test(title)) continue;
            seen.add(title);

            let number = '', instructor = '';
            // Course number pattern: digits.digits
            for (const line of lines) {
                if (!number) {
                    const nm = line.match(/(\d{1,2}\.\d{2,4}[A-Z]*)/);
                    if (nm) number = nm[1];
                }
                if (!instructor && /prof|dr\.|instructor/i.test(line)) instructor = line;
            }

            const fullUrl = href.startsWith('/') ? 'https://ocw.mit.edu' + href : href;
            results.push({ title: title.slice(0, 120), number, instructor, url: fullUrl });
        }

        return results;
    }""", request.max_results)

    courses = [Course(**d) for d in courses_data]
    result = CourseResult(courses=courses[:request.max_results])

    print("\n" + "=" * 60)
    print(f"MIT OCW: {request.query}")
    print("=" * 60)
    for i, c in enumerate(result.courses, 1):
        print(f"  {i}. {c.title}")
        if c.number:
            print(f"     Number:     {c.number}")
        if c.instructor:
            print(f"     Instructor: {c.instructor}")
        if c.url:
            print(f"     URL:        {c.url}")
    print(f"\nTotal: {len(result.courses)} courses")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("ocw_mit_edu")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = ocw_search(page, CourseRequest())
            print(f"\nReturned {len(result.courses)} courses")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
