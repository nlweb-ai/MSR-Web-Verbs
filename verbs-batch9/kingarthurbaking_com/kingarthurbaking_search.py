"""
Playwright script (Python) — King Arthur Baking Recipe Search
Search King Arthur Baking for recipes and extract details.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class KingArthurRequest:
    search_query: str = "sourdough bread"
    max_results: int = 5


@dataclass
class RecipeItem:
    title: str = ""
    reviews: str = ""


@dataclass
class KingArthurResult:
    query: str = ""
    items: List[RecipeItem] = field(default_factory=list)


# Searches King Arthur Baking for recipes matching the query and returns
# up to max_results recipes with title, rating, reviews, prep time, bake time, and difficulty.
def search_kingarthur_recipes(page: Page, request: KingArthurRequest) -> KingArthurResult:
    import urllib.parse
    url = f"https://www.kingarthurbaking.com/search?query={urllib.parse.quote_plus(request.search_query)}&tab=recipes"
    print(f"Loading {url}...")
    checkpoint("Navigate to King Arthur Baking search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = KingArthurResult(query=request.search_query)

    checkpoint("Extract recipe listings")
    js_code = """(max) => {
        const results = [];
        const lines = document.body.innerText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find "Recipes (N)" section
        let startIdx = -1;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].match(/^Recipes \\(\\d+\\)/)) { startIdx = i + 1; break; }
        }
        if (startIdx < 0) return results;
        // Parse recipe groups: title, (count), "Reviews" or "Review"
        for (let i = startIdx; i < lines.length && results.length < max; i++) {
            const title = lines[i];
            // Stop at next section
            if (title.match(/^(Blogs|Classes|Other|Products) \\(/)) break;
            if (title.match(/^\\+\\d+ MORE/)) break;
            // Check if next line is review count like "(849)"
            if (i + 1 < lines.length && lines[i + 1].match(/^\\(\\d+\\)$/)) {
                const reviews = lines[i + 1].replace(/[()]/g, '');
                results.push({ title, reviews });
                i += 2; // skip count + "Reviews"
            } else if (i + 1 < lines.length && lines[i + 1] === 'Not Reviewed Yet') {
                results.push({ title, reviews: '0' });
                i += 1;
            }
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = RecipeItem()
        item.title = d.get("title", "")
        item.reviews = d.get("reviews", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} recipes for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Reviews: {item.reviews}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("kingarthur")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_kingarthur_recipes(page, KingArthurRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} recipes")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
