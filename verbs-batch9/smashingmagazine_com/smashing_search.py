"""Playwright script (Python) — Smashing Magazine"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class SmashingRequest:
    query: str = "CSS Grid layout"
    max_results: int = 5

@dataclass
class ArticleItem:
    title: str = ""
    author: str = ""
    publish_date: str = ""
    summary: str = ""

@dataclass
class SmashingResult:
    articles: List[ArticleItem] = field(default_factory=list)

def search_smashing(page: Page, request: SmashingRequest) -> SmashingResult:
    url = f"https://www.smashingmagazine.com/search/?q={request.query.replace(' ', '+')}"
    checkpoint("Navigate to Smashing Magazine search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = SmashingResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: "Author wrote", Title, "date \u2014 summary"
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (/wrote$/.test(lines[i]) && i + 2 < lines.length) {
                const author = lines[i].replace(/ wrote$/, '');
                const title = lines[i + 1];
                const dateLine = lines[i + 2];
                const dashIdx = dateLine.indexOf('\u2014');
                let publish_date = '', summary = '';
                if (dashIdx > -1) {
                    publish_date = dateLine.substring(0, dashIdx).trim();
                    summary = dateLine.substring(dashIdx + 1).trim();
                }
                if (title.length > 10) {
                    results.push({ title, author, publish_date, summary });
                }
                i += 2;
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = ArticleItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.publish_date = d.get("publish_date", "")
        item.summary = d.get("summary", "")
        result.articles.append(item)

    print(f"\nFound {len(result.articles)} articles:")
    for i, a in enumerate(result.articles, 1):
        print(f"\n  {i}. {a.title}")
        print(f"     Author: {a.author}  Date: {a.publish_date}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("smashing")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_smashing(page, SmashingRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
