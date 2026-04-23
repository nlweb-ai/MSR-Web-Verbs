import os
import sys
import shutil
import time
from dataclasses import dataclass, field
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class PatchSearchRequest:
    search_query: str = "community events"
    max_results: int = 5


@dataclass
class PatchSearchItem:
    title: str = ""
    location: str = ""
    publish_date: str = ""
    summary: str = ""
    url: str = ""


@dataclass
class PatchSearchResult:
    items: List[PatchSearchItem] = field(default_factory=list)


def patch_search(page, request: PatchSearchRequest) -> PatchSearchResult:
    url = f"https://patch.com/search?q={request.search_query}"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    items = page.evaluate("""() => {
        const results = [];
        const articles = document.querySelectorAll('[class*="search-result"], [class*="card"], article, .story, [class*="article"]');
        for (let i = 0; i < articles.length; i++) {
            const el = articles[i];
            const titleEl = el.querySelector('h2 a, h3 a, [class*="title"] a, [class*="headline"] a');
            const locationEl = el.querySelector('[class*="location"], [class*="patch-name"], [class*="source"]');
            const dateEl = el.querySelector('time, [class*="date"], [class*="timestamp"]');
            const summaryEl = el.querySelector('[class*="summary"], [class*="description"], [class*="excerpt"], p');
            const linkEl = el.querySelector('a[href*="patch.com"]') || el.querySelector('h2 a, h3 a');
            results.push({
                title: titleEl ? titleEl.innerText.trim() : '',
                location: locationEl ? locationEl.innerText.trim() : '',
                publish_date: dateEl ? dateEl.innerText.trim() : '',
                summary: summaryEl ? summaryEl.innerText.trim() : '',
                url: linkEl ? linkEl.href : ''
            });
        }
        return results.filter(r => r.title);
    }""")

    result = PatchSearchResult()
    for item in items[: request.max_results]:
        result.items.append(
            PatchSearchItem(
                title=item.get("title", ""),
                location=item.get("location", ""),
                publish_date=item.get("publish_date", ""),
                summary=item.get("summary", ""),
                url=item.get("url", ""),
            )
        )

    checkpoint("patch_search result")
    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir()
    chrome_process = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(ws_url)
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()

    try:
        request = PatchSearchRequest(search_query="community events", max_results=5)
        result = patch_search(page, request)
        print(f"Found {len(result.items)} articles")
        for i, item in enumerate(result.items):
            print(f"  {i+1}. {item.title}")
            print(f"     Location: {item.location} | Date: {item.publish_date}")
            print(f"     {item.summary[:100]}...")
            print(f"     URL: {item.url}")
    finally:
        browser.close()
        pw.stop()
        chrome_process.terminate()
        shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger

    run_with_debugger(test_func)
