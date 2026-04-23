"""
Playwright script (Python) — Course Hero Search
Search for study resources on Course Hero.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CourseHeroSearchRequest:
    query: str = "organic chemistry"
    max_results: int = 5


@dataclass
class ResourceItem:
    title: str = ""
    course_code: str = ""
    school: str = ""
    resource_type: str = ""
    num_views: str = ""


@dataclass
class CourseHeroSearchResult:
    query: str = ""
    items: List[ResourceItem] = field(default_factory=list)


def search_coursehero(page: Page, request: CourseHeroSearchRequest) -> CourseHeroSearchResult:
    """Search Course Hero for study resources."""
    encoded = quote_plus(request.query)
    url = f"https://www.coursehero.com/search/results/?stx={encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = CourseHeroSearchResult(query=request.query)

    checkpoint("Extract resources")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('article');
        for (const card of cards) {
            if (items.length >= max) break;
            const lines = card.innerText.split('\\n').map(l => l.trim()).filter(l => l);
            if (lines.length < 3) continue;

            const title = lines[0];
            if (!title || title.length < 3) continue;

            // Find type line (COURSE, NOTES, DOCUMENT, etc.)
            let resType = '';
            let school = '';
            let courseCode = '';
            let views = '';
            for (let j = 1; j < lines.length; j++) {
                const line = lines[j];
                if (/^(COURSE|NOTES|DOCUMENT|STUDY GUIDE|HOMEWORK|EXAM|QUIZ|LECTURE|LAB)$/i.test(line)) {
                    resType = line;
                } else if (/^\\d+\\s+(course documents|views)/i.test(line)) {
                    const vm = line.match(/^(\\d+)\\s+views/i);
                    if (vm) views = vm[1];
                } else if (!courseCode && /^[A-Z]/.test(line) && line.length < 40 && j === 1) {
                    courseCode = line;
                } else if (!school && line.length > 5 && !resType && j > 2) {
                    school = line;
                }
            }
            // The line right after type is usually the school
            const typeIdx = lines.indexOf(resType);
            if (typeIdx >= 0 && typeIdx + 1 < lines.length && !school) {
                const candidate = lines[typeIdx + 1];
                if (candidate && !/^\\d+/.test(candidate)) school = candidate;
            }
            // For courses, school is the last non-type line
            if (!school && resType === 'COURSE' && lines.length > 4) {
                school = lines[lines.length - 1];
            }

            const key = title + '|' + school;
            if (items.some(i => (i.title + '|' + i.school) === key)) continue;

            items.push({title, course_code: courseCode, school, resource_type: resType, num_views: views});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ResourceItem()
        item.title = d.get("title", "")
        item.course_code = d.get("course_code", "")
        item.school = d.get("school", "")
        item.resource_type = d.get("resource_type", "")
        item.num_views = d.get("num_views", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} resources for '{request.query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Course: {item.course_code}  School: {item.school}  Type: {item.resource_type}  Views: {item.num_views}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("coursehero")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_coursehero(page, CourseHeroSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} resources")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
