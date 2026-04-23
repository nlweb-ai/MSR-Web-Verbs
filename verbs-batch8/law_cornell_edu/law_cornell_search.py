import os
import sys
import shutil
from dataclasses import dataclass, field
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class LawCornellSearchRequest:
    search_query: str = "first amendment"
    max_results: int = 5


@dataclass
class LawCornellSearchItem:
    title: str = ""
    code_section: str = ""
    jurisdiction: str = ""
    summary: str = ""
    url: str = ""


@dataclass
class LawCornellSearchResult:
    items: List[LawCornellSearchItem] = field(default_factory=list)
    query: str = ""
    result_count: int = 0


def law_cornell_search(page, request: LawCornellSearchRequest) -> LawCornellSearchResult:
    url = f"https://www.law.cornell.edu/wex/{request.search_query.replace(' ', '_')}"
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    raw_items = page.evaluate("""() => {
        const items = [];
        const seen = new Set();
        // First try to get main content links (articles within the topic)
        const mainContent = document.querySelector('#main-content, .field-item, article, .node-content') || document;
        const links = mainContent.querySelectorAll('a[href]');
        for (const a of links) {
            const href = a.getAttribute('href') || '';
            // Match wex article links (not category links)
            if (!/\\/wex\\/[a-z]/.test(href)) continue;
            if (/\\/wex\\/category\\//.test(href)) continue;
            if (seen.has(href)) continue;
            seen.add(href);
            const text = a.textContent.trim();
            if (!text || text.length < 5 || text.length > 200) continue;
            // Skip nav-like text
            if (/^(U\\.S\\. Code|CFR|Wex|Home|About|Menu|Search|Browse)/i.test(text)) continue;
            const fullUrl = href.startsWith('http') ? href : 'https://www.law.cornell.edu' + href;
            items.push({title: text, url: fullUrl, summary: ''});
        }
        // Fallback: get main content paragraphs
        if (items.length === 0) {
            const paras = document.querySelectorAll('#main-content p, .field-item p, article p');
            for (const p of paras) {
                const text = p.textContent.trim();
                if (text.length > 50) {
                    items.push({title: text.substring(0, 100), url: '', summary: text});
                    if (items.length >= 5) break;
                }
            }
        }
        return items;
    }""")

    checkpoint("Extracted search results")

    result = LawCornellSearchResult(query=request.search_query)
    for raw in raw_items[: request.max_results]:
        title = raw.get("title", "")
        # Try to parse code_section from the title
        code_section = ""
        jurisdiction = ""
        if "U.S.C." in title or "§" in title or "CFR" in title:
            code_section = title
            jurisdiction = "Federal"
        elif "Amend" in title or "Constitution" in title:
            jurisdiction = "U.S. Constitution"
        else:
            jurisdiction = "Federal"

        item = LawCornellSearchItem(
            title=title,
            code_section=code_section,
            jurisdiction=jurisdiction,
            summary=raw.get("summary", ""),
            url=raw.get("url", ""),
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
        request = LawCornellSearchRequest(search_query="first amendment", max_results=5)
        result = law_cornell_search(page, request)
        print(f"Query: {result.query}")
        print(f"Result count: {result.result_count}")
        for i, item in enumerate(result.items, 1):
            print(f"\n--- Result {i} ---")
            print(f"  Title: {item.title}")
            print(f"  Code Section: {item.code_section}")
            print(f"  Jurisdiction: {item.jurisdiction}")
            print(f"  Summary: {item.summary[:100]}...")
            print(f"  URL: {item.url}")
    finally:
        browser.close()
        pw.stop()
        chrome_proc.terminate()
        shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
