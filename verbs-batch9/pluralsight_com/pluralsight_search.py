"""
Playwright script (Python) — Pluralsight Course Search
Search Pluralsight for Kubernetes courses.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class PluralsightRequest:
    query: str = "Kubernetes"
    max_results: int = 5


@dataclass
class CourseItem:
    title: str = ""
    author: str = ""
    skill_level: str = ""
    date: str = ""


@dataclass
class PluralsightResult:
    courses: List[CourseItem] = field(default_factory=list)


# Searches Pluralsight for courses and extracts title,
# author, skill level, and date.
def search_pluralsight(page: Page, request: PluralsightRequest) -> PluralsightResult:
    url = f"https://www.pluralsight.com/search?q={request.query.replace(' ', '+')}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Pluralsight search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)

    result = PluralsightResult()

    checkpoint("Extract course listings")
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find 'Courses' section header
        let start = 0;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === 'Courses' && i > 10) { start = i + 1; break; }
        }
        const levels = ['Beginner', 'Intermediate', 'Advanced'];
        const seen = new Set();
        for (let i = start; i < lines.length && results.length < max; i++) {
            // Check if next line starts with 'by ' (author) → this line is title
            if (i + 3 < lines.length && /^by /.test(lines[i + 1]) && levels.includes(lines[i + 2])) {
                const title = lines[i];
                if (seen.has(title)) continue;
                seen.add(title);
                const author = lines[i + 1];
                const skill_level = lines[i + 2];
                const date = lines[i + 3] || '';
                // Stop if we hit Labs section
                if (/^View \\d+ matching/i.test(lines[i + 4] || '') || lines[i + 4] === 'Labs') {
                    results.push({ title, author, skill_level, date });
                    break;
                }
                results.push({ title, author, skill_level, date });
                i += 3;
            }
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = CourseItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.skill_level = d.get("skill_level", "")
        item.date = d.get("date", "")
        result.courses.append(item)

    print(f"\nFound {len(result.courses)} courses:")
    for i, c in enumerate(result.courses, 1):
        print(f"\n  {i}. {c.title}")
        print(f"     Author: {c.author}  Level: {c.skill_level}  Date: {c.date}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("pluralsight")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_pluralsight(page, PluralsightRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.courses)} courses")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
