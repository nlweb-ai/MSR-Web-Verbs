"""Playwright script (Python) — WebMD"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class WebMDRequest:
    query: str = "Type 2 Diabetes"
    max_results: int = 5

@dataclass
class ArticleItem:
    title: str = ""
    article_type: str = ""
    description: str = ""

@dataclass
class WebMDResult:
    articles: List[ArticleItem] = field(default_factory=list)

def search_webmd(page: Page, request: WebMDRequest) -> WebMDResult:
    url = f"https://www.webmd.com/search/search_results/default.aspx?query={request.query.replace(' ', '+')}"
    checkpoint("Navigate to WebMD search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = WebMDResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: "Article"/"Drug"/"Slideshow"/"Quiz" → Title → Description
        const types = new Set(['Article', 'Drug', 'Slideshow', 'Quiz', 'Video', 'Page']);
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (types.has(lines[i]) && i + 2 < lines.length) {
                const title = lines[i + 1];
                const description = lines[i + 2];
                if (title && title.length > 5 && !types.has(title)) {
                    results.push({ title, article_type: lines[i], description });
                }
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = ArticleItem()
        item.title = d.get("title", "")
        item.article_type = d.get("article_type", "")
        item.description = d.get("description", "")
        result.articles.append(item)

    print(f"\nFound {len(result.articles)} articles:")
    for i, a in enumerate(result.articles, 1):
        print(f"  {i}. [{a.article_type}] {a.title} - {a.description[:60]}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("webmd")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_webmd(page, WebMDRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
