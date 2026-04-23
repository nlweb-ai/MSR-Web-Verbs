"""Playwright script (Python) — wikiHow"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class WikiHowRequest:
    query: str = "how to start a garden"
    max_results: int = 5

@dataclass
class ArticleItem:
    title: str = ""
    views: str = ""
    updated: str = ""

@dataclass
class WikiHowResult:
    articles: List[ArticleItem] = field(default_factory=list)

def search_wikihow(page: Page, request: WikiHowRequest) -> WikiHowResult:
    url = f"https://www.wikihow.com/wikiHowTo?search={request.query.replace(' ', '+')}"
    checkpoint("Navigate to wikiHow search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    result = WikiHowResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: Title → "X views" → "Updated X ago" → optional "Expert Co-Authored"
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i].endsWith(' views') && i >= 1 && i + 1 < lines.length) {
                const title = lines[i - 1];
                const views = lines[i];
                const updated = lines[i + 1];
                if (title && title.length > 10 && updated.startsWith('Updated ')) {
                    results.push({ title, views, updated });
                }
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = ArticleItem()
        item.title = d.get("title", "")
        item.views = d.get("views", "")
        item.updated = d.get("updated", "")
        result.articles.append(item)

    print(f"\nFound {len(result.articles)} articles:")
    for i, a in enumerate(result.articles, 1):
        print(f"  {i}. {a.title} - {a.views} - {a.updated}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("wikihow")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_wikihow(page, WikiHowRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
