import os
import sys
import shutil
from dataclasses import dataclass, field
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class NamiSearchRequest:
    search_query: str = "depression"
    max_results: int = 5


@dataclass
class NamiSearchItem:
    title: str = ""
    category: str = ""
    summary: str = ""
    url: str = ""
    resource_type: str = ""


@dataclass
class NamiSearchResult:
    items: List[NamiSearchItem] = field(default_factory=list)
    query: str = ""
    result_count: int = 0


def nami_search(page, request: NamiSearchRequest) -> NamiSearchResult:
    url = f"https://www.nami.org/search?s={request.search_query.replace(' ', '+')}"
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)

    raw_items = page.evaluate("""() => {
        const items = [];
        const results = document.querySelectorAll('.search-results .result, .search-result, article, .result-item, .post, li.search-item, [class*="SearchResult"]');
        for (const el of results) {
            const titleEl = el.querySelector('h2 a, h3 a, .title a, h2, h3, a[class*="title"]');
            const summaryEl = el.querySelector('.excerpt, .summary, p, .description, .snippet');
            const categoryEl = el.querySelector('[class*="category"], [class*="tag"], .type, [class*="label"]');
            const linkEl = el.querySelector('a[href]');

            const title = titleEl ? titleEl.textContent.trim() : '';
            if (!title) continue;

            const href = linkEl ? linkEl.href : '';
            // Try to infer resource_type from URL or category
            let resourceType = '';
            if (href.includes('/blog')) resourceType = 'Blog Post';
            else if (href.includes('/fact-sheet') || href.includes('/learn')) resourceType = 'Fact Sheet';
            else if (href.includes('/guide')) resourceType = 'Guide';
            else resourceType = 'Article';

            items.push({
                title: title,
                category: categoryEl ? categoryEl.textContent.trim() : '',
                summary: summaryEl ? summaryEl.textContent.trim().substring(0, 200) : '',
                url: href,
                resource_type: resourceType,
            });
        }
        return items;
    }""")

    checkpoint("Extracted NAMI search results")

    result = NamiSearchResult(query=request.search_query)
    for raw in raw_items[: request.max_results]:
        item = NamiSearchItem(
            title=raw.get("title", ""),
            category=raw.get("category", ""),
            summary=raw.get("summary", ""),
            url=raw.get("url", ""),
            resource_type=raw.get("resource_type", ""),
        )
        result.items.append(item)

    result.result_count = len(result.items)
    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir()
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(ws_url)
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()

    try:
        request = NamiSearchRequest(search_query="depression", max_results=5)
        result = nami_search(page, request)
        print(f"Query: {result.query}")
        print(f"Result count: {result.result_count}")
        for i, item in enumerate(result.items, 1):
            print(f"\n--- Result {i} ---")
            print(f"  Title: {item.title}")
            print(f"  Category: {item.category}")
            print(f"  Summary: {item.summary[:100]}...")
            print(f"  URL: {item.url}")
            print(f"  Resource Type: {item.resource_type}")
    finally:
        browser.close()
        pw.stop()
        chrome_proc.terminate()
        shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
