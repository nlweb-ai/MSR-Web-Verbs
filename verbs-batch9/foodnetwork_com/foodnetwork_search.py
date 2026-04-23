"""
Playwright script (Python) — Food Network Recipe Search
Search for recipes on FoodNetwork.com.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class FoodNetworkSearchRequest:
    search_query: str = "chocolate cake"
    max_results: int = 5


@dataclass
class RecipeItem:
    name: str = ""
    chef: str = ""
    reviews: str = ""
    total_time: str = ""
    reviews: str = ""


@dataclass
class FoodNetworkSearchResult:
    query: str = ""
    items: List[RecipeItem] = field(default_factory=list)


# Searches FoodNetwork.com for recipes matching the query and returns
# up to max_results recipes with name, chef, rating, reviews, prep time, and difficulty.
def search_foodnetwork_recipes(page: Page, request: FoodNetworkSearchRequest) -> FoodNetworkSearchResult:
    import urllib.parse
    slug = urllib.parse.quote_plus(request.search_query).replace('%20', '-').replace('+', '-')
    url = f"https://www.foodnetwork.com/search/{slug}-"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = FoodNetworkSearchResult(query=request.search_query)

    checkpoint("Extract recipe listings")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        const cards = document.querySelectorAll('section.o-RecipeResult, .m-MediaBlock');
        for (const card of cards) {
            if (results.length >= max) break;
            const lines = card.innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 2) continue;
            const name = lines[0].trim();
            if (!name || name.length < 3 || seen.has(name)) continue;
            seen.add(name);
            let chef = '', total_time = '', reviews = '';
            for (const l of lines) {
                const t = l.trim();
                if (t.startsWith('RECIPE | Courtesy of ')) chef = t.replace('RECIPE | Courtesy of ', '');
                if (t.startsWith('Total Time:')) total_time = t.replace('Total Time: ', '');
                if (t.endsWith('Reviews')) reviews = t.replace(' Reviews', '');
            }
            results.push({name, chef, total_time, reviews});
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = RecipeItem()
        item.name = d.get("name", "")
        item.chef = d.get("chef", "")
        item.reviews = d.get("reviews", "")
        item.total_time = d.get("total_time", "")
        item.reviews = d.get("reviews", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} recipes for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name}")
        print(f"     Chef: {item.chef}  Reviews: {item.reviews}")
        print(f"     Total time: {item.total_time}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("foodnetwork")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_foodnetwork_recipes(page, FoodNetworkSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} recipes")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
