"""
Auto-generated Playwright script (Python)
Class Central – Course Search
Query: "data science"

Generated on: 2026-04-18T05:04:39.344Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CourseRequest:
    query: str = "data science"
    max_courses: int = 5


@dataclass
class Course:
    title: str = ""
    provider: str = ""
    institution: str = ""
    rating: str = ""
    reviews: str = ""


@dataclass
class CourseResult:
    courses: list = field(default_factory=list)


def classcentral_search(page: Page, request: CourseRequest) -> CourseResult:
    """Search Class Central for online courses."""
    print(f"  Query: {request.query}\n")

    url = f"https://www.classcentral.com/search?q={quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Class Central search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract course listings")
    courses_data = page.evaluate(r"""(maxCourses) => {
        const results = [];
        const items = document.querySelectorAll(
            '[class*="course"], [class*="catalog-card"], article, li[class*="row"]'
        );
        const seen = new Set();
        for (const item of items) {
            if (results.length >= maxCourses) break;
            const titleEl = item.querySelector('h2, h3, h4, [class*="name"], [class*="title"]');
            const title = titleEl ? titleEl.innerText.trim() : '';
            if (!title || title.length < 5 || seen.has(title)) continue;
            seen.add(title);

            const text = item.innerText || '';
            let provider = '', institution = '', rating = '', reviews = '';

            const provM = text.match(/(Coursera|edX|Udacity|FutureLearn|Udemy|Swayam|Khan Academy)/i);
            if (provM) provider = provM[1];

            const instM = text.match(/(?:via|from|by)\s+([A-Z][^\n]{3,50})/i);
            if (instM) institution = instM[1].trim();

            const ratM = text.match(/(\d+\.\d)\s*(?:\/\s*5|stars?|rating)/i);
            if (ratM) rating = ratM[1];

            const revM = text.match(/(\d[\d,]*)\s*(?:review|rating)/i);
            if (revM) reviews = revM[1];

            results.push({ title, provider, institution, rating, reviews });
        }
        return results;
    }""", request.max_courses)

    result = CourseResult(courses=[Course(**c) for c in courses_data])

    print("\n" + "=" * 60)
    print(f"Class Central: {request.query}")
    print("=" * 60)
    for c in result.courses:
        print(f"  {c.title}")
        print(f"    Provider: {c.provider}  Institution: {c.institution}")
        print(f"    Rating: {c.rating}  Reviews: {c.reviews}")
    print(f"\n  Total: {len(result.courses)} courses")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("classcentral_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = classcentral_search(page, CourseRequest())
            print(f"\nReturned {len(result.courses)} courses")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
