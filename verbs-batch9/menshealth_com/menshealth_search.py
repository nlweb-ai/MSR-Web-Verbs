"""
Playwright script (Python) — Men's Health Article Search
Search Men's Health for fitness articles.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MensHealthRequest:
    query: str = "strength training for beginners"
    max_results: int = 5


@dataclass
class ArticleItem:
    title: str = ""
    author: str = ""
    date: str = ""
    category: str = ""
    summary: str = ""


@dataclass
class MensHealthResult:
    articles: List[ArticleItem] = field(default_factory=list)


# Searches Men's Health for fitness articles and extracts title,
# author, publish date, category, and summary.
def search_menshealth(page: Page, request: MensHealthRequest) -> MensHealthResult:
    url = f"https://www.menshealth.com/search/?q={request.query.replace(' ', '+')}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Men's Health search")
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)

    result = MensHealthResult()

    checkpoint("Extract articles from search results")
    js_code = """(max) => {
        const results = [];
        // Try standard selectors first
        const items = document.querySelectorAll('.simple-item, .result-item, article, [class*="search-result"]');
        for (const item of items) {
            if (results.length >= max) break;
            const titleEl = item.querySelector('h2 a, h3 a, a[class*="title"]');
            const title = titleEl ? titleEl.textContent.trim() : '';
            if (!title) continue;

            const authorEl = item.querySelector('[class*="author"], .byline, span[class*="name"]');
            const author = authorEl ? authorEl.textContent.trim() : '';

            const dateEl = item.querySelector('time, [class*="date"], [class*="published"]');
            const date = dateEl ? dateEl.textContent.trim() : '';

            const catEl = item.querySelector('[class*="category"], [class*="tag"]');
            const category = catEl ? catEl.textContent.trim() : '';

            const summaryEl = item.querySelector('[class*="description"], [class*="summary"], p');
            const summary = summaryEl ? summaryEl.textContent.trim().substring(0, 200) : '';

            results.push({ title, author, date, category, summary });
        }
        if (results.length > 0) return results;

        // Fallback: text-based parsing
        const text = document.body.innerText;
        const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        const datePattern = /^[A-Z]{3}\\s+\\d{1,2},\\s+\\d{4}$/;
        for (let i = 0; i < lines.length; i++) {
            if (results.length >= max) break;
            if (datePattern.test(lines[i])) {
                // Look backwards for title
                let title = '';
                for (let j = i - 1; j >= Math.max(0, i - 5); j--) {
                    if (lines[j].length > 15 && !/^by /i.test(lines[j])) {
                        title = lines[j];
                        break;
                    }
                }
                if (!title) continue;
                // Look for author nearby
                let author = '';
                for (let j = i - 3; j <= i + 2; j++) {
                    if (j >= 0 && j < lines.length && /^by /i.test(lines[j])) {
                        author = lines[j].replace(/^by\\s+/i, '');
                        break;
                    }
                }
                const date = lines[i];
                // Look for summary after date
                let summary = '';
                if (i + 1 < lines.length && lines[i + 1].length > 30) {
                    summary = lines[i + 1].substring(0, 200);
                }
                results.push({ title, author, date, category: '', summary });
            }
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ArticleItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.date = d.get("date", "")
        item.category = d.get("category", "")
        item.summary = d.get("summary", "")
        result.articles.append(item)

    print(f"\nFound {len(result.articles)} articles:")
    for i, a in enumerate(result.articles, 1):
        print(f"\n  {i}. {a.title}")
        print(f"     Author: {a.author}  Date: {a.date}")
        print(f"     Category: {a.category}")
        print(f"     Summary: {a.summary[:100]}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("menshealth")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_menshealth(page, MensHealthRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
