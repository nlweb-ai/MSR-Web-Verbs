import os
import sys
import shutil
from dataclasses import dataclass, field
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MyfontsSearchRequest:
    search_query: str = "serif"
    max_results: int = 5


@dataclass
class MyfontsSearchItem:
    font_name: str = ""
    foundry: str = ""
    price: str = ""


@dataclass
class MyfontsSearchResult:
    items: List[MyfontsSearchItem] = field(default_factory=list)
    query: str = ""
    result_count: int = 0


def myfonts_search(page, request: MyfontsSearchRequest) -> MyfontsSearchResult:
    url = f"https://www.myfonts.com/search?query={request.search_query.replace(' ', '+')}"
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)

    raw_items = page.evaluate("""(max) => {
        const items = [];
        const seen = new Set();
        const lines = document.body.innerText.split('\\n').map(l => l.trim()).filter(l => l);
        for (let i = 0; i < lines.length && items.length < max; i++) {
            if (lines[i] === 'By' && i >= 2) {
                const foundry = lines[i + 1] || '';
                const priceLine = (i + 2 < lines.length && lines[i + 2].includes('$')) ? lines[i + 2] : '';
                const price = priceLine.replace(/^From\\s+/, '').replace(/\\s+USD$/, '');
                const font_name = lines[i - 2] || '';
                if (!font_name || font_name.length < 2 || seen.has(font_name)) continue;
                if (font_name.match(/^(Price|Styles|Languages|Foundries|Visual|Advanced|Not able|Sign|Subscribe|Relevance|Images)/i)) continue;
                seen.add(font_name);
                items.push({ font_name, foundry, price, num_styles: '', classification: '', sample_text: '' });
            }
        }
        return items;
    }""", request.max_results)

    checkpoint("Extracted font search results")

    result = MyfontsSearchResult(query=request.search_query)
    for raw in raw_items[: request.max_results]:
        item = MyfontsSearchItem(
            font_name=raw.get("font_name", ""),
            foundry=raw.get("foundry", ""),
            price=raw.get("price", ""),
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
        request = MyfontsSearchRequest(search_query="serif", max_results=5)
        result = myfonts_search(page, request)
        print(f"Query: {result.query}")
        print(f"Result count: {result.result_count}")
        for i, item in enumerate(result.items, 1):
            print(f"\n--- Result {i} ---")
            print(f"  Font Name: {item.font_name}")
            print(f"  Foundry: {item.foundry}")
            print(f"  Price: {item.price}")
    finally:
        browser.close()
        pw.stop()
        chrome_proc.terminate()
        shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
