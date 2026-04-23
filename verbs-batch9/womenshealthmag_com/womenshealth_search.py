"""Playwright script (Python) — Women's Health"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class WomensHealthRequest:
    query: str = "fitness"
    max_results: int = 5

@dataclass
class ArticleItem:
    title: str = ""
    date: str = ""

@dataclass
class WomensHealthResult:
    articles: List[ArticleItem] = field(default_factory=list)

def search_womenshealth(page: Page, request: WomensHealthRequest) -> WomensHealthResult:
    url = f"https://www.womenshealthmag.com/{request.query.replace(' ', '-').lower()}/"
    checkpoint("Navigate to Women's Health category")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = WomensHealthResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: Title → Date (e.g. "Apr 13, 2026") or Title → optional read time → Date
        const dateRe = /^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\s+\\d+,\\s+\\d{4}$/;
        const skip = /^(Advertisement|Skip to|Newsletter|Search|Sign in|Subscribe|Fitness|Health|Beauty|Product|Sports|Video|Membership|About|US$)/;
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (dateRe.test(lines[i]) && i >= 1) {
                // Title is 1 or 2 lines before date
                let title = lines[i - 1];
                // Skip "X min" read time
                if (/^\\d+\\s+min$/.test(title) && i >= 2) {
                    title = lines[i - 2];
                }
                // Skip "By Author" lines — title is 2 before "By", not 1
                if (title.startsWith('By ') && i >= 3) {
                    title = lines[i - 3];
                } else if (title.startsWith('By ') && i >= 2) {
                    title = lines[i - 2];
                }
                if (!title || title.length < 15 || skip.test(title)) continue;
                results.push({ title, date: lines[i] });
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = ArticleItem()
        item.title = d.get("title", "")
        item.date = d.get("date", "")
        result.articles.append(item)

    print(f"\nFound {len(result.articles)} articles:")
    for i, a in enumerate(result.articles, 1):
        print(f"  {i}. {a.title} - {a.date}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("womenshealth")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_womenshealth(page, WomensHealthRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
