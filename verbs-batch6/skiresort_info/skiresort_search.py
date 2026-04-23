"""Auto-generated – Skiresort.info – Ski Resort Search – Query: "best ski resorts Alps" """
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class ResortRequest:
    query: str = "best ski resorts Alps"
    max_results: int = 5

@dataclass
class Resort:
    title: str = ""
    url: str = ""

@dataclass
class ResortResult:
    items: List[Resort] = field(default_factory=list)

def skiresort_search(page: Page, request: ResortRequest) -> ResortResult:
    print(f"  Query: {request.query}\n")
    from urllib.parse import quote_plus
    url = f"https://www.google.com/search?q=site%3Askiresort.info+{quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Google site search for Skiresort.info")
    page.goto(url, wait_until="domcontentloaded"); page.wait_for_timeout(3000)
    data = page.evaluate(r"""(m) => {
        const r = [], s = new Set();
        for (const h of document.querySelectorAll('h3')) {
            if (r.length >= m) break;
            let t = h.innerText.trim().replace(/\s*[\|\u2013\u2014-]\s*Skiresort.*$/i, '').trim();
            if (t.length < 5 || s.has(t)) continue; s.add(t);
            let u = ''; const a = h.closest('a') || h.parentElement?.closest('a');
            if (a) u = a.href || '';
            r.push({ title: t.slice(0, 150), url: u });
        } return r;
    }""", request.max_results)
    items = [Resort(**d) for d in data]
    result = ResortResult(items=items[:request.max_results])
    print("\n" + "=" * 60)
    print(f"Skiresort.info: {request.query}")
    print("=" * 60)
    for i, item in enumerate(result.items, 1):
        print(f"  {i}. {item.title}")
        if item.url: print(f"     URL: {item.url}")
    print(f"\nTotal: {len(result.items)} items")
    return result

def test_func():
    port = get_free_port(); profile_dir = get_temp_profile_dir("skiresort_info")
    chrome_proc = launch_chrome(profile_dir, port); ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url); context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = skiresort_search(page, ResortRequest())
            print(f"\nReturned {len(result.items)} items")
        finally: browser.close(); chrome_proc.terminate(); shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
