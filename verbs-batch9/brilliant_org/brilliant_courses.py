"""
Playwright script (Python) — Brilliant.org Courses
Browse courses on Brilliant.org by category.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BrilliantCoursesRequest:
    category: str = "Mathematics"
    max_results: int = 5


@dataclass
class CourseItem:
    name: str = ""


@dataclass
class BrilliantCoursesResult:
    category: str = ""
    items: List[CourseItem] = field(default_factory=list)


def browse_brilliant_courses(page: Page, request: BrilliantCoursesRequest) -> BrilliantCoursesResult:
    """Browse Brilliant.org courses by category."""
    url = "https://brilliant.org/courses/#math"
    print(f"Loading {url}...")
    checkpoint("Navigate to courses")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = BrilliantCoursesResult(category=request.category)

    checkpoint("Extract courses")
    js_code = """(max) => {
        const items = [];
        const links = document.querySelectorAll('a[href*="/courses/"]');
        for (const a of links) {
            if (items.length >= max) break;
            const name = a.innerText.trim();
            if (!name || name.length < 3 || name === 'Courses') continue;
            if (items.some(i => i.name === name)) continue;
            items.push({name: name});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = CourseItem()
        item.name = d.get("name", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} courses in '{request.category}':")
    for i, item in enumerate(result.items, 1):
        print(f"  {i}. {item.name}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("brilliant")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = browse_brilliant_courses(page, BrilliantCoursesRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} courses")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
