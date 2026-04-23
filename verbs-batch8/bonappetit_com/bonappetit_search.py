"""
Bon Appetit – Search for recipes

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BonAppetitSearchRequest:
    search_query: str = "pasta"
    max_results: int = 5


@dataclass
class BonAppetitRecipeItem:
    recipe_name: str = ""
    author: str = ""
    rating: str = ""
    total_time: str = ""
    description: str = ""
    image_url: str = ""


@dataclass
class BonAppetitSearchResult:
    items: List[BonAppetitRecipeItem] = field(default_factory=list)


# Search for recipes on Bon Appetit.
def bonappetit_search(page: Page, request: BonAppetitSearchRequest) -> BonAppetitSearchResult:
    """Search for recipes on Bon Appetit."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://www.bonappetit.com/search?q={query}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Bon Appetit search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = BonAppetitSearchResult()

    checkpoint("Extract recipe listings")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();
        
        // Strategy 1: Find links to recipe pages
        const links = document.querySelectorAll('a[href*="/recipe/"]');
        for (const a of links) {
            if (items.length >= max) break;
            const title = a.innerText.trim().split('\\n')[0].trim();
            if (title.length < 5 || seen.has(title)) continue;
            seen.add(title);
            
            const card = a.closest('div[class], li, article') || a;
            const fullText = card.innerText.trim();
            const lines = fullText.split('\\n').filter(l => l.trim());
            
            let author = '';
            let description = '';
            for (const line of lines) {
                if (line.toLowerCase().startsWith('by ')) author = line.replace(/^by\\s+/i, '');
                if (line.length > 30 && line !== title && !description) description = line.substring(0, 200);
            }
            
            items.push({recipe_name: title, author, rating: '', total_time: '', description, image_url: ''});
        }
        
        // Strategy 2: headings
        if (items.length === 0) {
            const headings = document.querySelectorAll('h2, h3');
            for (const h of headings) {
                if (items.length >= max) break;
                const title = h.innerText.trim();
                if (title.length > 5 && !seen.has(title)) {
                    seen.add(title);
                    items.push({recipe_name: title, author: '', rating: '', total_time: '', description: '', image_url: ''});
                }
            }
        }
        
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = BonAppetitRecipeItem()
        item.recipe_name = d.get("recipe_name", "")
        item.author = d.get("author", "")
        item.rating = d.get("rating", "")
        item.total_time = d.get("total_time", "")
        item.description = d.get("description", "")
        item.image_url = d.get("image_url", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Recipe {i}:")
        print(f"    Name:        {item.recipe_name}")
        print(f"    Author:      {item.author}")
        print(f"    Rating:      {item.rating}")
        print(f"    Time:        {item.total_time}")
        print(f"    Description: {item.description[:100]}...")
        print(f"    Image:       {item.image_url[:80]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("bonappetit")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = BonAppetitSearchRequest()
            result = bonappetit_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} recipes")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
