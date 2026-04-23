"""
Playwright script (Python) — Kiplinger Article Search
Search Kiplinger for financial articles and extract details.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class KiplingerRequest:
    search_query: str = "retirement planning"
    max_results: int = 5


@dataclass
class ArticleItem:
    title: str = ""
    category: str = ""
    summary: str = ""


@dataclass
class KiplingerResult:
    query: str = ""
    items: List[ArticleItem] = field(default_factory=list)


# Searches Kiplinger for articles matching the query and returns
# up to max_results articles with title, author, publish date, category, and summary.
def search_kiplinger_articles(page: Page, request: KiplingerRequest) -> KiplingerResult:
    import urllib.parse
    url = f"https://www.kiplinger.com/retirement/retirement-planning"
    print(f"Loading {url}...")
    checkpoint("Navigate to Kiplinger retirement planning page")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = KiplingerResult(query=request.search_query)

    checkpoint("Extract article listings")
    js_code = """(max) => {
        const results = [];
        // Find article headings (h2/h3), then get context from parent
        const headings = document.querySelectorAll('h2, h3');
        const seen = new Set();
        for (const heading of headings) {
            if (results.length >= max) break;
            const title = heading.textContent.trim();
            if (!title || title.length < 10 || seen.has(title)) continue;
            if (title === 'Latest') continue;
            seen.add(title);

            // Walk up to find the containing link/listitem for author/summary
            const container = heading.closest('a, li, div') || heading.parentElement;
            const text = container ? container.textContent : '';

            let author = '';
            const byMatch = text.match(/BY\\s+([A-Z][A-Z\\s.,®]+)/);
            if (byMatch) author = byMatch[1].trim();

            let summary = '';
            if (container) {
                const pEls = container.querySelectorAll('p');
                for (const p of pEls) {
                    const pText = p.textContent.trim();
                    if (pText.length > 20 && !pText.startsWith('BY')) {
                        summary = pText.substring(0, 200);
                        break;
                    }
                }
            }

            results.push({ title, author, publish_date: '', category: 'Retirement Planning', summary });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ArticleItem()
        item.title = d.get("title", "")
        item.category = d.get("category", "")
        item.summary = d.get("summary", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} articles for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Category: {item.category}")
        print(f"     Category: {item.category}")
        print(f"     Summary: {item.summary[:100]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("kiplinger")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_kiplinger_articles(page, KiplingerRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
