"""Auto-generated – Google Scholar – Academic Paper Search – Query: "deep learning neural networks" """
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class PaperRequest:
    query: str = "deep learning neural networks"
    max_results: int = 5

@dataclass
class Paper:
    title: str = ""
    url: str = ""

@dataclass
class PaperResult:
    items: List[Paper] = field(default_factory=list)

def scholar_search(page: Page, request: PaperRequest) -> PaperResult:
    print(f"  Query: {request.query}\n")
    from urllib.parse import quote_plus
    url = f"https://scholar.google.com/scholar?q={quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Google Scholar search")
    page.goto(url, wait_until="domcontentloaded"); page.wait_for_timeout(3000)
    data = page.evaluate(r"""(m) => {
        const r = [], s = new Set();
        for (const h of document.querySelectorAll('.gs_ri h3')) {
            if (r.length >= m) break;
            let t = h.innerText.trim().replace(/\s*[\|\u2013\u2014-]\s*Google\s*Scholar.*$/i, '').trim();
            if (t.length < 5 || s.has(t)) continue; s.add(t);
            let u = ''; const a = h.closest('a') || h.parentElement?.closest('a');
            if (a) u = a.href || '';
            r.push({ title: t.slice(0, 150), url: u });
        } return r;
    }""", request.max_results)
    items = [Paper(**d) for d in data]
    result = PaperResult(items=items[:request.max_results])
    print("\n" + "=" * 60)
    print(f"Google Scholar: {request.query}")
    print("=" * 60)
    for i, item in enumerate(result.items, 1):
        print(f"  {i}. {item.title}")
        if item.url: print(f"     URL: {item.url}")
    print(f"\nTotal: {len(result.items)} items")
    return result

def test_func():
    port = get_free_port(); profile_dir = get_temp_profile_dir("scholar_google_com__search")
    chrome_proc = launch_chrome(profile_dir, port); ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url); context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = scholar_search(page, PaperRequest())
            print(f"\nReturned {len(result.items)} items")
        finally: browser.close(); chrome_proc.terminate(); shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
