"""
Playwright script (Python) — NYT Cooking Recipe Search
Search NYT Cooking for chicken soup recipes.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class NYTRequest:
    query: str = "chicken soup"
    max_results: int = 5


@dataclass
class RecipeItem:
    name: str = ""
    author: str = ""
    rating: str = ""
    num_ratings: str = ""
    prep_time: str = ""


@dataclass
class NYTResult:
    recipes: List[RecipeItem] = field(default_factory=list)


# Searches NYT Cooking for recipes and extracts recipe name,
# author, rating, number of ratings, and prep time.
def search_nyt_recipes(page: Page, request: NYTRequest) -> NYTResult:
    url = f"https://cooking.nytimes.com/search?q={request.query.replace(' ', '+')}"
    print(f"Loading {url}...")
    checkpoint("Navigate to NYT Cooking search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = NYTResult()

    checkpoint("Extract recipe results")
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        const start = lines.findIndex(l => l === 'SEARCH RESULTS');
        if (start < 0) return results;
        // Parse groups: Title, Author, "N ratings with...", "N,NNN", "time", optional "EASY"
        const ratingRe = /^\\d+ ratings with an average rating of (\\d+) out of 5/;
        let i = start + 1;
        while (i < lines.length && results.length < max) {
            const name = lines[i];
            if (!name || name.length < 3 || /^(Show|Load|Page|\\d)/.test(name)) { i++; continue; }
            const author = lines[i + 1] || '';
            const ratingLine = lines[i + 2] || '';
            const rMatch = ratingLine.match(ratingRe);
            const rating = rMatch ? rMatch[1] + '/5' : '';
            const numRatings = lines[i + 3] || '';
            const timeLine = lines[i + 4] || '';
            const prep_time = /min|hour/i.test(timeLine) ? timeLine : '';
            results.push({ name, author, rating, num_ratings: numRatings, prep_time });
            // Skip past this recipe (5 lines + optional EASY tag)
            i += 5;
            if (i < lines.length && /^EASY$/i.test(lines[i])) i++;
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = RecipeItem()
        item.name = d.get("name", "")
        item.author = d.get("author", "")
        item.rating = d.get("rating", "")
        item.num_ratings = d.get("num_ratings", "")
        item.prep_time = d.get("prep_time", "")
        result.recipes.append(item)

    print(f"\nFound {len(result.recipes)} recipes:")
    for i, r in enumerate(result.recipes, 1):
        print(f"\n  {i}. {r.name}")
        print(f"     Author: {r.author}  Rating: {r.rating}  Time: {r.prep_time}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("nyt")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_nyt_recipes(page, NYTRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.recipes)} recipes")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
