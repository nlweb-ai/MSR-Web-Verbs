"""
Playwright script (Python) — Figma Community Search
Search for design files on Figma Community.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class FigmaCommunitySearchRequest:
    search_query: str = "dashboard"
    max_results: int = 5


@dataclass
class FigmaFileItem:
    name: str = ""
    creator: str = ""
    likes: str = ""
    duplicates: str = ""


@dataclass
class FigmaCommunitySearchResult:
    query: str = ""
    items: List[FigmaFileItem] = field(default_factory=list)


# Searches Figma Community for design files matching the query and returns
# up to max_results files with name, creator, likes, and duplicates count.
def search_figma_community(page: Page, request: FigmaCommunitySearchRequest) -> FigmaCommunitySearchResult:
    import urllib.parse
    url = f"https://www.figma.com/community/search?resource_type=mixed&sort_by=relevancy&query={urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Figma Community search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = FigmaCommunitySearchResult(query=request.search_query)

    checkpoint("Extract design file listings")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        const allLinks = document.querySelectorAll('a[href*="/community/file/"]');
        for (const link of allLinks) {
            if (results.length >= max) break;
            const parent = link.closest('div') || link;
            const lines = parent.innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 4) continue;
            const name = lines[0].trim();
            if (!name || name.length < 3 || seen.has(name)) continue;
            seen.add(name);
            let creator = '';
            if (lines[1] && lines[1].startsWith('by ')) creator = lines[1].replace('by ', '').trim();
            const likes = lines[3] ? lines[3].trim() : '';
            const duplicates = lines[4] ? lines[4].trim() : '';
            results.push({name, creator, likes, duplicates});
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = FigmaFileItem()
        item.name = d.get("name", "")
        item.creator = d.get("creator", "")
        item.likes = d.get("likes", "")
        item.duplicates = d.get("duplicates", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} files for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name}")
        print(f"     Creator: {item.creator}  Likes: {item.likes}  Duplicates: {item.duplicates}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("figma")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_figma_community(page, FigmaCommunitySearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} files")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
