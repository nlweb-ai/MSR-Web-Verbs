"""
Playwright script (Python) — edX Course Search
Search edX for online courses.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class EdxSearchRequest:
    search_query: str = "data science"
    max_results: int = 5


@dataclass
class CourseItem:
    name: str = ""
    institution: str = ""
    duration: str = ""
    level: str = ""


@dataclass
class EdxSearchResult:
    query: str = ""
    items: List[CourseItem] = field(default_factory=list)


def search_edx(page: Page, request: EdxSearchRequest) -> EdxSearchResult:
    """Search edX for online courses."""
    url = f"https://www.edx.org/search?q={request.search_query.replace(' ', '+')}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = EdxSearchResult(query=request.search_query)

    checkpoint("Extract courses")
    js_code = """(max) => {
        const items = [];
        // Find the "Courses" section
        const h3s = document.querySelectorAll('h3');
        for (const h3 of h3s) {
            if (h3.textContent.trim() !== 'Courses') continue;
            const gp = h3.parentElement.parentElement;
            const scrollDiv = gp.children[1];
            if (!scrollDiv) continue;
            const flexRow = scrollDiv.children[0];
            if (!flexRow) continue;
            for (let i = 0; i < flexRow.children.length && items.length < max; i++) {
                const card = flexRow.children[i];
                const lines = card.innerText.split('\\n').filter(l => l.trim());
                if (lines.length < 3) continue;
                const courseType = lines[0].trim();
                const name = lines[1] ? lines[1].trim() : '';
                const institution = lines[2] ? lines[2].trim() : '';
                const duration = lines[3] ? lines[3].trim() : '';
                const level = lines[4] ? lines[4].trim() : '';
                if (!name || name.length < 3) continue;
                items.push({name, institution, level, duration});
            }
            break;
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = CourseItem()
        item.name = d.get("name", "")
        item.institution = d.get("institution", "")
        item.duration = d.get("duration", "")
        item.level = d.get("level", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} courses for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name}")
        print(f"     Institution: {item.institution}  Level: {item.level}")
        print(f"     Duration: {item.duration}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("edx")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_edx(page, EdxSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} courses")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
