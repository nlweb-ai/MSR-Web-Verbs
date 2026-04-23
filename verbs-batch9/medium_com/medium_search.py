"""
Playwright script (Python) — Medium Article Search
Search Medium for articles and extract details.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MediumRequest:
    query: str = "startup fundraising"
    max_results: int = 5


@dataclass
class ArticleItem:
    title: str = ""
    author: str = ""
    summary: str = ""


@dataclass
class MediumResult:
    articles: List[ArticleItem] = field(default_factory=list)


# Searches Medium for articles and extracts title, author, and summary.
def search_medium(page: Page, request: MediumRequest) -> MediumResult:
    url = f"https://medium.com/search?q={request.query.replace(' ', '+')}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Medium search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = MediumResult()

    checkpoint("Extract articles from search results")
    js_code = """(max) => {
        const results = [];
        const articles = document.querySelectorAll('article, div[data-testid="postPreview"]');
        const seen = new Set();
        for (const art of articles) {
            if (results.length >= max) break;
            const h2 = art.querySelector('h2');
            const title = h2 ? h2.textContent.trim() : '';
            if (!title || seen.has(title)) continue;
            seen.add(title);
            const lines = art.innerText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            let author = '';
            // Pattern 1: "In PUBLICATION by Author Title..." 
            // Pattern 2: "Author Title Summary Date"
            if (lines[0] === 'In' && lines.length > 3) {
                // Find "by" line, author is next
                for (let k = 0; k < lines.length; k++) {
                    if (lines[k] === 'by' && k + 1 < lines.length) { author = lines[k + 1]; break; }
                }
            } else {
                author = lines[0] || '';
            }
            // Summary: line after title that's long enough
            let summary = '';
            let foundTitle = false;
            for (const line of lines) {
                if (line === title) { foundTitle = true; continue; }
                if (foundTitle && line.length > 20) { summary = line.substring(0, 200); break; }
            }
            results.push({ title, author, summary });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ArticleItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.summary = d.get("summary", "")
        result.articles.append(item)

    print(f"\nFound {len(result.articles)} articles:")
    for i, a in enumerate(result.articles, 1):
        print(f"\n  {i}. {a.title}")
        print(f"     Author: {a.author}")
        print(f"     Summary: {a.summary[:80]}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("medium")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_medium(page, MediumRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
