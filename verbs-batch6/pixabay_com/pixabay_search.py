"""Auto-generated – Pixabay Image Search – Query: "ocean waves" """
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class ImageRequest:
    query: str = "ocean waves"
    max_results: int = 5

@dataclass
class ImageItem:
    title: str = ""
    url: str = ""

@dataclass
class ImageResult:
    images: List[ImageItem] = field(default_factory=list)

def pixabay_search(page: Page, request: ImageRequest) -> ImageResult:
    print(f"  Query: {request.query}\n")
    from urllib.parse import quote_plus
    url = f"https://www.google.com/search?q=site%3Apixabay.com+{quote_plus(request.query)}+image"
    print(f"Loading {url}...")
    checkpoint("Google site search for Pixabay")
    page.goto(url, wait_until="domcontentloaded"); page.wait_for_timeout(3000)
    data = page.evaluate(r"""(m) => {
        const r = [], s = new Set();
        for (const h of document.querySelectorAll('h3')) {
            if (r.length >= m) break;
            let t = h.innerText.trim().replace(/\s*[\|\u2013\u2014-]\s*Pixabay.*$/i, '').trim();
            if (t.length < 5 || s.has(t)) continue; s.add(t);
            let u = ''; const a = h.closest('a') || h.parentElement?.closest('a');
            if (a) u = a.href || '';
            r.push({ title: t.slice(0, 150), url: u });
        } return r;
    }""", request.max_results)
    images = [ImageItem(**d) for d in data]
    result = ImageResult(images=images[:request.max_results])
    print("\n" + "=" * 60)
    print(f"Pixabay: {request.query}")
    print("=" * 60)
    for i, img in enumerate(result.images, 1):
        print(f"  {i}. {img.title}")
        if img.url: print(f"     URL: {img.url}")
    print(f"\nTotal: {len(result.images)} images")
    return result

def test_func():
    port = get_free_port(); profile_dir = get_temp_profile_dir("pixabay_com")
    chrome_proc = launch_chrome(profile_dir, port); ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url); context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = pixabay_search(page, ImageRequest())
            print(f"\nReturned {len(result.images)} images")
        finally: browser.close(); chrome_proc.terminate(); shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
