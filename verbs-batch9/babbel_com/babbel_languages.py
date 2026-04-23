"""
Playwright script (Python) — Babbel Languages
Browse available languages on Babbel.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BabbelLanguagesRequest:
    max_results: int = 5


@dataclass
class LanguageItem:
    language_name: str = ""


@dataclass
class BabbelLanguagesResult:
    items: List[LanguageItem] = field(default_factory=list)


def browse_babbel_languages(page: Page, request: BabbelLanguagesRequest) -> BabbelLanguagesResult:
    """Browse available languages on Babbel."""
    url = "https://www.babbel.com"
    print(f"Loading {url}...")
    checkpoint("Navigate to Babbel homepage")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = BabbelLanguagesResult()

    checkpoint("Extract languages")
    js_code = """(max) => {
        const items = [];
        const links = document.querySelectorAll('a[href*="/learn-"], [class*="language"], [class*="Language"]');
        const seen = new Set();
        for (const el of links) {
            if (items.length >= max) break;
            const name = el.textContent.trim();
            if (!name || name.length < 3 || name.length > 30 || seen.has(name)) continue;
            seen.add(name);
            const href = el.getAttribute('href') || '';
            items.push({language_name: name});
        }
        if (items.length === 0) {
            const body = document.body.innerText;
            const langNames = ['Spanish', 'French', 'German', 'Italian', 'Portuguese', 'Russian', 'Turkish', 'Dutch', 'Swedish', 'Polish', 'Norwegian', 'Danish', 'Indonesian', 'English'];
            for (const lang of langNames) {
                if (items.length >= max) break;
                if (body.includes(lang)) {
                    items.push({language_name: lang});
                }
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = LanguageItem()
        item.language_name = d.get("language_name", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} languages:")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.language_name}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("babbel")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = browse_babbel_languages(page, BabbelLanguagesRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} languages")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
