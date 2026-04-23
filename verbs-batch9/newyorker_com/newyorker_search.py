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
class NewyorkerSearchRequest:
    search_query: str = "technology"
    max_results: int = 5


@dataclass
class NewyorkerSearchItem:
    title: str = ""
    author: str = ""
    publish_date: str = ""
    section: str = ""
    summary: str = ""


@dataclass
class NewyorkerSearchResult:
    items: List[NewyorkerSearchItem] = field(default_factory=list)


def newyorker_search(page, request: NewyorkerSearchRequest) -> NewyorkerSearchResult:
    url = f"https://www.newyorker.com/search?q={request.search_query.replace(' ', '+')}&sort=relevance"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    items = page.evaluate("""(max) => {
        const results = [];
        const lines = document.body.innerText.split('\\n').map(l => l.trim()).filter(l => l);
        // Find articles by "By Author" pattern
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i].startsWith('By ') && i >= 2) {
                const author = lines[i].replace(/^By\\s+/, '');
                const dateLine = (i + 1 < lines.length) ? lines[i + 1] : '';
                if (!dateLine.match(/\\w+\\s+\\d{1,2},\\s+\\d{4}/)) continue;
                const summary = lines[i - 1] || '';
                const title = lines[i - 2] || '';
                if (title.length < 10) continue;
                // Section: check line before title
                const section = (i >= 3 && lines[i - 3].length < 30 && !lines[i - 3].startsWith('By ')) ? lines[i - 3] : '';
                results.push({ title, author, publish_date: dateLine, section, summary: summary.substring(0, 200) });
            }
        }
        return results;
    }""", request.max_results)

    result = NewyorkerSearchResult()
    for item in items[: request.max_results]:
        result.items.append(
            NewyorkerSearchItem(
                title=item.get("title", ""),
                author=item.get("author", ""),
                publish_date=item.get("publish_date", ""),
                section=item.get("section", ""),
                summary=item.get("summary", ""),
            )
        )

    checkpoint("newyorker_search result")
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
        request = NewyorkerSearchRequest(search_query="technology", max_results=5)
        result = newyorker_search(page, request)
        print(f"Found {len(result.items)} articles")
        for i, item in enumerate(result.items):
            print(f"  {i+1}. {item.title} by {item.author} ({item.publish_date})")
            print(f"     Section: {item.section}")
            print(f"     {item.summary[:100]}...")
    finally:
        browser.close()
        pw.stop()
        chrome_process.terminate()
        shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger

    run_with_debugger(test_func)
