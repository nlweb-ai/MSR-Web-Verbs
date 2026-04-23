"""
Auto-generated Playwright script (Python)
Comic Vine – Search for comic book characters by keyword
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ComicvineSearchRequest:
    search_query: str = "Spider-Man"
    max_results: int = 5


@dataclass
class ComicvineCharacterItem:
    character_name: str = ""
    real_name: str = ""
    publisher: str = ""
    first_appearance: str = ""
    description: str = ""
    num_appearances: str = ""


@dataclass
class ComicvineSearchResult:
    items: List[ComicvineCharacterItem] = field(default_factory=list)


# Search for comic book characters on Comic Vine by keyword.
def comicvine_search(page: Page, request: ComicvineSearchRequest) -> ComicvineSearchResult:
    """Search for comic book characters on Comic Vine."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://comicvine.gamespot.com/search/?q={query}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Comic Vine search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = ComicvineSearchResult()

    checkpoint("Extract character listings")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();
        
        // Strategy 1: find links to character/comic pages
        const links = document.querySelectorAll('a[href]');
        for (const a of links) {
            if (items.length >= max) break;
            const href = a.getAttribute('href') || '';
            // Comic Vine links like /4005-1234/
            if (!href.match(/\\/4\\d{3}-\\d+/) && !href.includes('/character/') && !href.includes('/issue/')) continue;
            
            const title = a.innerText.trim().split('\\n')[0].trim();
            if (title.length < 3 || title.length > 100 || seen.has(title)) continue;
            seen.add(title);
            
            const card = a.closest('li, div, tr, article') || a;
            const fullText = card.innerText.trim();
            const lines = fullText.split('\\n').filter(l => l.trim());
            
            let desc = '';
            for (const line of lines) {
                if (line.length > 30 && line !== title && !desc) desc = line.substring(0, 200);
            }
            
            items.push({character_name: title, real_name: '', publisher: '', first_appearance: '', description: desc, num_appearances: ''});
        }
        
        // Strategy 2: heading-based
        if (items.length === 0) {
            const headings = document.querySelectorAll('h2, h3');
            for (const h of headings) {
                if (items.length >= max) break;
                const title = h.innerText.trim();
                if (title.length > 3 && !seen.has(title)) {
                    seen.add(title);
                    items.push({character_name: title, real_name: '', publisher: '', first_appearance: '', description: '', num_appearances: ''});
                }
            }
        }
        
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ComicvineCharacterItem()
        item.character_name = d.get("character_name", "")
        item.real_name = d.get("real_name", "")
        item.publisher = d.get("publisher", "")
        item.first_appearance = d.get("first_appearance", "")
        item.description = d.get("description", "")
        item.num_appearances = d.get("num_appearances", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Character {i}:")
        print(f"    Name:        {item.character_name}")
        print(f"    Real Name:   {item.real_name}")
        print(f"    Publisher:   {item.publisher}")
        print(f"    First App:   {item.first_appearance}")
        print(f"    Description: {item.description[:100]}...")
        print(f"    Appearances: {item.num_appearances}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("comicvine")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = ComicvineSearchRequest()
            result = comicvine_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} characters")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
