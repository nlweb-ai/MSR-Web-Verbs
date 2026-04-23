"""
Playwright script (Python) — InfoQ Article Search
Search InfoQ for tech articles.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class InfoQRequest:
    search_query: str = "microservices architecture"
    max_results: int = 5


@dataclass
class ArticleItem:
    title: str = ""
    publish_date: str = ""
    topic: str = ""
    summary: str = ""


@dataclass
class InfoQResult:
    query: str = ""
    items: List[ArticleItem] = field(default_factory=list)


def search_infoq(page: Page, request: InfoQRequest) -> InfoQResult:
    import urllib.parse
    url = f"https://www.infoq.com/search.action?queryString={urllib.parse.quote_plus(request.search_query)}&page=1&searchOrder=relevance"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = InfoQResult(query=request.search_query)

    checkpoint("Extract article listings")
    js_code = """(max) => {
        const results = [];
        const lines = document.body.innerText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find "Page results for" marker
        let startIdx = 0;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].startsWith('Page results for')) { startIdx = i + 1; break; }
        }
        // Skip "Order results by:", "View by relevance", "View by date"
        while (startIdx < lines.length && lines[startIdx].match(/^(Order results|View by)/i)) startIdx++;
        // Parse 3-line groups: title, "date ... summary", url
        for (let i = startIdx; i + 2 < lines.length && results.length < max; i++) {
            const title = lines[i];
            const dateSummary = lines[i + 1];
            const url = lines[i + 2];
            // URL line must start with http
            if (!url.startsWith('http')) continue;
            // Parse date from "Jul 28, 2023 ... summary text"
            let publish_date = '';
            let summary = dateSummary;
            const dateMatch = dateSummary.match(/^([A-Z][a-z]+ \\d{1,2}, \\d{4})/);
            if (dateMatch) {
                publish_date = dateMatch[1];
                summary = dateSummary.replace(/^[A-Z][a-z]+ \\d{1,2}, \\d{4}\\s*\\.{3}\\s*/, '');
            }
            // Extract topic from URL path (e.g. /articles/, /presentations/, /news/)
            let topic = '';
            const topicMatch = url.match(/infoq\\.com\\/(articles|presentations|news|podcasts|minibooks)/);
            if (topicMatch) topic = topicMatch[1];
            if (title.length < 10) continue;
            results.push({ title: title.replace(/ - InfoQ$/, ''), author: '', publish_date, topic, summary: summary.substring(0, 200) });
            i += 2; // skip to next group
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ArticleItem()
        item.title = d.get("title", "")
        item.publish_date = d.get("publish_date", "")
        item.topic = d.get("topic", "")
        item.summary = d.get("summary", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} articles for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Date: {item.publish_date}")
        print(f"     Topic: {item.topic}")
        if item.summary:
            print(f"     {item.summary[:100]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("infoq")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_infoq(page, InfoQRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
