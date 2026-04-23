import os
import sys
import shutil
from dataclasses import dataclass, field
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MinimalistBakerSearchRequest:
    search_query: str = "vegan pasta"
    max_results: int = 5


@dataclass
class MinimalistBakerSearchItem:
    recipe_name: str = ""
    total_time: str = ""
    servings: str = ""
    rating: str = ""
    description: str = ""
    diet_tags: str = ""


@dataclass
class MinimalistBakerSearchResult:
    items: List[MinimalistBakerSearchItem] = field(default_factory=list)
    query: str = ""
    result_count: int = 0


def minimalistbaker_search(page, request: MinimalistBakerSearchRequest) -> MinimalistBakerSearchResult:
    url = f"https://minimalistbaker.com/?s={request.search_query.replace(' ', '+')}"
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)

    raw_items = page.evaluate("""() => {
        const items = [];
        const posts = document.querySelectorAll('article, .post-summary, .archive-post, .entry, .search-result');
        for (const post of posts) {
            const titleEl = post.querySelector('h2 a, h3 a, .entry-title a, h2, h3');
            const descEl = post.querySelector('.entry-content p, .post-summary__description, .excerpt, p');
            const timeEl = post.querySelector('.time, .duration, [class*="time"]');
            const ratingEl = post.querySelector('[class*="rating"], .wprm-recipe-rating');
            const tagEl = post.querySelector('[class*="tag"], [class*="category"], .diet-tag');

            const name = titleEl ? titleEl.textContent.trim() : '';
            if (!name) continue;

            items.push({
                recipe_name: name,
                total_time: timeEl ? timeEl.textContent.trim() : '',
                servings: '',
                rating: ratingEl ? ratingEl.textContent.trim() : '',
                description: descEl ? descEl.textContent.trim().substring(0, 200) : '',
                diet_tags: tagEl ? tagEl.textContent.trim() : '',
            });
        }
        return items;
    }""")

    checkpoint("Extracted recipe results")

    result = MinimalistBakerSearchResult(query=request.search_query)
    for raw in raw_items[: request.max_results]:
        item = MinimalistBakerSearchItem(
            recipe_name=raw.get("recipe_name", ""),
            total_time=raw.get("total_time", ""),
            servings=raw.get("servings", ""),
            rating=raw.get("rating", ""),
            description=raw.get("description", ""),
            diet_tags=raw.get("diet_tags", ""),
        )
        result.items.append(item)

    result.result_count = len(result.items)
    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir()
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(ws_url)
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()

    try:
        request = MinimalistBakerSearchRequest(search_query="vegan pasta", max_results=5)
        result = minimalistbaker_search(page, request)
        print(f"Query: {result.query}")
        print(f"Result count: {result.result_count}")
        for i, item in enumerate(result.items, 1):
            print(f"\n--- Result {i} ---")
            print(f"  Recipe: {item.recipe_name}")
            print(f"  Total Time: {item.total_time}")
            print(f"  Servings: {item.servings}")
            print(f"  Rating: {item.rating}")
            print(f"  Description: {item.description[:100]}...")
            print(f"  Diet Tags: {item.diet_tags}")
    finally:
        browser.close()
        pw.stop()
        chrome_proc.terminate()
        shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
