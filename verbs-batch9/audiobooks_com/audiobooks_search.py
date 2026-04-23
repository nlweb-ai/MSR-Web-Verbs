"""
Playwright script (Python) — Audiobooks.com Search
Browse audiobooks by genre on Audiobooks.com.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class AudiobooksSearchRequest:
    genre: str = "mystery"
    max_results: int = 5


@dataclass
class AudiobookItem:
    title: str = ""
    author: str = ""
    duration: str = ""
    price: str = ""


@dataclass
class AudiobooksSearchResult:
    genre: str = ""
    items: List[AudiobookItem] = field(default_factory=list)


def search_audiobooks(page: Page, request: AudiobooksSearchRequest) -> AudiobooksSearchResult:
    """Browse audiobooks by genre."""
    url = f"https://www.audiobooks.com/search?keywords={request.genre}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = AudiobooksSearchResult(genre=request.genre)

    checkpoint("Extract audiobooks")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('li, [class*="book"], [class*="item"], [class*="result"]');
        for (const card of cards) {
            if (items.length >= max) break;
            const lines = card.innerText.split('\\n').map(l => l.trim()).filter(l => l);
            let duration = '';
            for (const line of lines) {
                const dm = line.match(/^(\\d+\\s*hr\\s*\\d*\\s*min)$/i);
                if (dm) { duration = dm[1]; break; }
            }
            if (!duration) continue;
            const titleEl = card.querySelector('a h3, a h2, h3 a, h2 a, h3, h2');
            let title = '';
            if (titleEl) {
                title = titleEl.innerText.split('\\n')[0].trim();
            }
            if (!title || title.length < 3) {
                title = lines[0] || '';
            }
            if (title === duration || title.match(/^\\d+\\s*hr/i)) continue;
            if (items.some(i => i.title === title)) continue;
            let author = '';
            for (const line of lines) {
                if (line === title || line === duration) continue;
                if (line.match(/^\\$/)) continue;
                if (line.length > 3 && line.length < 80 && !line.match(/credit|sign|\\$|browse/i)) {
                    author = line;
                    break;
                }
            }
            let price = '';
            for (const line of lines) {
                const pm = line.match(/^(\\$[\\d.]+)$/);
                if (pm) { price = pm[1]; break; }
            }
            items.push({title, author, duration, price});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = AudiobookItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.duration = d.get("duration", "")
        item.price = d.get("price", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} audiobooks in '{request.genre}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Author: {item.author}  Duration: {item.duration}  Price: {item.price}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("audiobooks")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_audiobooks(page, AudiobooksSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} audiobooks")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
