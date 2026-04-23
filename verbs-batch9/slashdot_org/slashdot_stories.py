"""Playwright script (Python) — Slashdot"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class SlashdotRequest:
    max_results: int = 5

@dataclass
class StoryItem:
    headline: str = ""
    department: str = ""
    author: str = ""
    comments: str = ""
    post_date: str = ""

@dataclass
class SlashdotResult:
    stories: List[StoryItem] = field(default_factory=list)

def get_slashdot_stories(page: Page, request: SlashdotRequest) -> SlashdotResult:
    url = "https://slashdot.org/"
    checkpoint("Navigate to Slashdot")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    result = SlashdotResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Parse story blocks: headline, comment count, "Posted by X on DATE from the DEPT dept."
        const postedRe = /^Posted by (.+?) on (.+?) from the (.+?) dept\\.?$/;
        for (let i = 0; i < lines.length && results.length < max; i++) {
            const m = lines[i].match(postedRe);
            if (m && i >= 2) {
                const author = m[1];
                const post_date = m[2];
                const department = m[3];
                // Comment count is line before, headline is line before that
                const comments = lines[i - 1] || '';
                const headline = lines[i - 2] || '';
                // Skip sponsored/ad items
                if (/Sponsored|Slashdot$/i.test(author)) continue;
                if (headline.length > 10) {
                    results.push({ headline, author, department, comments, post_date });
                }
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = StoryItem()
        item.headline = d.get("headline", "")
        item.department = d.get("department", "")
        item.author = d.get("author", "")
        item.comments = d.get("comments", "")
        item.post_date = d.get("post_date", "")
        result.stories.append(item)

    print(f"\nFound {len(result.stories)} stories:")
    for i, s in enumerate(result.stories, 1):
        print(f"\n  {i}. {s.headline}")
        print(f"     Author: {s.author}  Dept: {s.department}  Comments: {s.comments}  Date: {s.post_date}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("slashdot")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            get_slashdot_stories(page, SlashdotRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
