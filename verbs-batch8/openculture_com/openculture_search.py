import os
import sys
import shutil
import time
from dataclasses import dataclass, field
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class OpencultureSearchRequest:
    search_query: str = "philosophy"
    max_results: int = 5


@dataclass
class OpencultureSearchItem:
    course_name: str = ""
    institution: str = ""
    instructor: str = ""
    subject: str = ""
    format: str = ""
    url: str = ""


@dataclass
class OpencultureSearchResult:
    items: List[OpencultureSearchItem] = field(default_factory=list)


def openculture_search(page, request: OpencultureSearchRequest) -> OpencultureSearchResult:
    url = f"https://www.openculture.com/?s={request.search_query}+free+online+courses"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    items = page.evaluate("""(max) => {
        const results = [];
        const seen = new Set();
        const links = document.querySelectorAll('a[href]');
        for (const a of links) {
            if (results.length >= max) break;
            const href = a.getAttribute('href') || '';
            // Match openculture article URLs with date pattern
            if (!href.match(/openculture\\.com\\/\\d{4}\\/\\d{2}\\//)) continue;
            const text = a.textContent.trim();
            if (!text || text.length < 15 || text.length > 200) continue;
            if (seen.has(href)) continue;
            seen.add(href);
            results.push({
                course_name: text,
                institution: '',
                instructor: '',
                subject: '',
                format: 'Online Course',
                url: href
            });
        }
        return results;
    }""", request.max_results)

    result = OpencultureSearchResult()
    for item in items[: request.max_results]:
        result.items.append(
            OpencultureSearchItem(
                course_name=item.get("course_name", ""),
                institution=item.get("institution", ""),
                instructor=item.get("instructor", ""),
                subject=item.get("subject", "") or request.search_query,
                format=item.get("format", ""),
                url=item.get("url", ""),
            )
        )

    checkpoint("openculture_search result")
    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir()
    chrome_process = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(ws_url)
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()

    try:
        request = OpencultureSearchRequest(search_query="philosophy", max_results=5)
        result = openculture_search(page, request)
        print(f"Found {len(result.items)} courses")
        for i, item in enumerate(result.items):
            print(f"  {i+1}. {item.course_name}")
            print(f"     Institution: {item.institution} | Subject: {item.subject} | Format: {item.format}")
            print(f"     URL: {item.url}")
    finally:
        browser.close()
        pw.stop()
        chrome_process.terminate()
        shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger

    run_with_debugger(test_func)
