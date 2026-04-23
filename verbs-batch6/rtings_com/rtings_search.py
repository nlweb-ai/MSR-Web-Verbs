"""Auto-generated – RTINGS – Product Review Search – Query: "best 4K TV 2024" """
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class ReviewRequest:
    query: str = "best 4K TV 2024"
    max_results: int = 5

@dataclass
class Review:
    title: str = ""
    url: str = ""

@dataclass
class ReviewResult:
    items: List[Review] = field(default_factory=list)

def rtings_search(page: Page, request: ReviewRequest) -> ReviewResult:
    print(f"  Query: {request.query}\n")
    from urllib.parse import quote_plus
    url = f"https://www.google.com/search?q=site%3Artings.com+{quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Google site search for RTINGS")
    page.goto(url, wait_until="domcontentloaded"); page.wait_for_timeout(3000)
    data = page.evaluate(r"""(m) => {
        const r = [], s = new Set();
        for (const h of document.querySelectorAll('h3')) {
            if (r.length >= m) break;
            let t = h.innerText.trim().replace(/\s*[\|\u2013\u2014-]\s*RTINGS.*$/i, '').trim();
            if (t.length < 5 || s.has(t)) continue; s.add(t);
            let u = ''; const a = h.closest('a') || h.parentElement?.closest('a');
            if (a) u = a.href || '';
            r.push({ title: t.slice(0, 150), url: u });
        } return r;
    }""", request.max_results)
    items = [Review(**d) for d in data]
    result = ReviewResult(items=items[:request.max_results])
    print("\n" + "=" * 60)
    print(f"RTINGS: {request.query}")
    print("=" * 60)
    for i, item in enumerate(result.items, 1):
        print(f"  {i}. {item.title}")
        if item.url: print(f"     URL: {item.url}")
    print(f"\nTotal: {len(result.items)} items")
    return result

def test_func():
    port = get_free_port(); profile_dir = get_temp_profile_dir("rtings_com")
    chrome_proc = launch_chrome(profile_dir, port); ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url); context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = rtings_search(page, ReviewRequest())
            print(f"\nReturned {len(result.items)} items")
        finally: browser.close(); chrome_proc.terminate(); shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
