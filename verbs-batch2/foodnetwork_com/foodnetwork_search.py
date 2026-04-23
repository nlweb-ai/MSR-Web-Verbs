"""
Playwright script (Python) — Food Network Recipe Search
Search for recipes matching a query, extract name, rating, and total time.

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class FoodNetworkSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class FoodNetworkRecipe:
    name: str
    rating: str
    total_time: str


@dataclass(frozen=True)
class FoodNetworkSearchResult:
    query: str
    recipes: list[FoodNetworkRecipe]


# Searches Food Network for recipes matching a query and extracts up to
# max_results recipes with name, rating, and total time.
def search_foodnetwork_recipes(
    page: Page,
    request: FoodNetworkSearchRequest,
) -> FoodNetworkSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    results: list[FoodNetworkRecipe] = []

    try:
        print("Loading Food Network...")
        url = f"https://www.foodnetwork.com/search/{query.replace(' ', '-')}-"
        checkpoint(f"Navigate to {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        for selector in [
            "button#onetrust-accept-btn-handler",
            "button:has-text('Accept')",
            "button:has-text('Close')",
        ]:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {selector}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        # ── STEP 1: Extract recipes ───────────────────────────────────────
        print(f'STEP 1: Extract up to {max_results} recipes for "{query}"...')

        h3s = page.locator("h3")
        count = h3s.count()
        print(f"  Found {count} headings")

        for i in range(count):
            if len(results) >= max_results:
                break
            h3 = h3s.nth(i)
            try:
                name = h3.inner_text(timeout=2000).strip()
                if not name:
                    continue
                parent_text = h3.evaluate(
                    "el => el.parentElement.innerText"
                )
                rating_match = re.search(r"(\d+)\s+Reviews", parent_text)
                rating = f"{rating_match.group(1)} Reviews" if rating_match else "N/A"
                time_match = re.search(r"Total Time:\s*(.+?)(?:\n|$)", parent_text)
                total_time = time_match.group(1).strip() if time_match else "N/A"

                if "RECIPE" in parent_text or time_match:
                    results.append(FoodNetworkRecipe(
                        name=name,
                        rating=rating,
                        total_time=total_time,
                    ))
                    print(f"  {len(results)}. {name} | Rating: {rating} | Time: {total_time}")
            except Exception as e:
                print(f"  Error on h3 {i}: {e}")
                continue

        print(f"\nFound {len(results)} recipes for '{query}':")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name}")
            print(f"     Rating: {r.rating}  Total Time: {r.total_time}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return FoodNetworkSearchResult(
        query=query,
        recipes=results,
    )


def test_search_foodnetwork_recipes() -> None:
    request = FoodNetworkSearchRequest(
        query="pasta",
        max_results=5,
    )

    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=False,
            viewport=None,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_foodnetwork_recipes(page, request)
            assert result.query == request.query
            assert len(result.recipes) <= request.max_results
            print(f"\nTotal recipes found: {len(result.recipes)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_foodnetwork_recipes)
