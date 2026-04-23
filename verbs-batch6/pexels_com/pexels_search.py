"""
Auto-generated Playwright script (Python)
Pexels – Stock Photo Search
Query: "mountain sunset"
"""
import re, os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class PhotoRequest:
    query: str = "mountain sunset"
    max_results: int = 5

@dataclass
class Photo:
    title: str = ""
    url: str = ""

@dataclass
class PhotoResult:
    photos: List[Photo] = field(default_factory=list)

def pexels_search(page: Page, request: PhotoRequest) -> PhotoResult:
    print(f"  Query: {request.query}\n")
    from urllib.parse import quote_plus
    url = f"https://www.google.com/search?q=site%3Apexels.com+{quote_plus(request.query)}+photo"
    print(f"Loading {url}...")
    checkpoint("Navigate to Google site search for Pexels")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    checkpoint("Extract photo listings")
    data = page.evaluate(r"""(maxResults) => {
        const results = [], seen = new Set();
        const h3s = document.querySelectorAll('h3');
        for (const h of h3s) {
            if (results.length >= maxResults) break;
            let t = h.innerText.trim().replace(/\s*[\|\u2013\u2014-]\s*Pexels.*$/i, '').trim();
            if (t.length < 5 || seen.has(t)) continue;
            seen.add(t);
            let url = '';
            const link = h.closest('a') || h.parentElement?.closest('a');
            if (link) url = link.href || '';
            results.push({ title: t.slice(0, 150), url });
        }
        return results;
    }""", request.max_results)
    photos = [Photo(**d) for d in data]
    result = PhotoResult(photos=photos[:request.max_results])
    print("\n" + "=" * 60)
    print(f"Pexels: {request.query}")
    print("=" * 60)
    for i, p in enumerate(result.photos, 1):
        print(f"  {i}. {p.title}")
        if p.url: print(f"     URL: {p.url}")
    print(f"\nTotal: {len(result.photos)} photos")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("pexels_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = pexels_search(page, PhotoRequest())
            print(f"\nReturned {len(result.photos)} photos")
        finally:
            browser.close(); chrome_proc.terminate(); shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
