"""
Playwright script (Python) — Khan Academy Course Browser
Browse Khan Academy courses in a given domain and extract course details.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class KhanAcademyRequest:
    domain: str = "computing"
    max_results: int = 5


@dataclass
class CourseItem:
    title: str = ""
    url: str = ""


@dataclass
class KhanAcademyResult:
    domain: str = ""
    items: List[CourseItem] = field(default_factory=list)


# Browses Khan Academy courses in the specified domain and returns
# up to max_results courses with title, unit count, estimated time, and description.
def browse_khanacademy_courses(page: Page, request: KhanAcademyRequest) -> KhanAcademyResult:
    url = f"https://www.khanacademy.org/{request.domain}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Khan Academy domain page")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = KhanAcademyResult(domain=request.domain)

    checkpoint("Extract course listings")
    js_code = """(args) => {
        const [max, domain] = args;
        const results = [];
        const cards = document.querySelectorAll('a[href*="/' + domain + '/"]');
        const seen = new Set();
        for (const card of cards) {
            if (results.length >= max) break;
            let title = card.textContent.trim().split('\\n')[0].trim();
            if (!title || title.length < 3 || seen.has(title)) continue;
            seen.add(title);
            const url = card.href || '';
            results.push({ title, url });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, [request.max_results, request.domain])

    for d in items_data:
        item = CourseItem()
        item.title = d.get("title", "")
        item.url = d.get("url", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} courses in '{request.domain}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     URL: {item.url}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("khanacademy")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = browse_khanacademy_courses(page, KhanAcademyRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} courses")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
