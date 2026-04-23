"""
Playwright script (Python) — Allrecipes.com Recipe Search
Search for recipes matching a query, extract name, rating, and total cook time.

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
class AllrecipesSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class AllrecipesRecipe:
    name: str
    rating: str
    cook_time: str


@dataclass(frozen=True)
class AllrecipesSearchResult:
    query: str
    recipes: list[AllrecipesRecipe]


# Searches Allrecipes.com for recipes matching a query, then extracts
# up to max_results recipes with name, rating, and total cook time.
def search_allrecipes(
    page: Page,
    request: AllrecipesSearchRequest,
) -> AllrecipesSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    results: list[AllrecipesRecipe] = []

    try:
        # ── Navigate ──────────────────────────────────────────────────────
        print("Loading Allrecipes.com...")
        checkpoint("Navigate to https://www.allrecipes.com")
        page.goto("https://www.allrecipes.com")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # ── Dismiss popups / cookie banners ───────────────────────────────
        for selector in [
            "button#onetrust-accept-btn-handler",
            "button:has-text('Accept')",
            "button:has-text('Got it')",
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

        # ── STEP 1: Search ────────────────────────────────────────────────
        print(f'STEP 1: Search for "{query}"...')
        search_input = page.locator(
            'input#search-input, '
            'input[name="search"], '
            'input[aria-label*="search" i], '
            'input[placeholder*="search" i]'
        ).first
        checkpoint("Click search input")
        search_input.evaluate("el => el.click()")
        page.wait_for_timeout(500)
        page.keyboard.press("Control+a")
        checkpoint(f"Type query: {query}")
        search_input.type(query, delay=50)
        page.wait_for_timeout(1000)
        checkpoint("Press Enter to search")
        page.keyboard.press("Enter")
        print(f'  Typed "{query}" and pressed Enter')
        page.wait_for_timeout(2000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # ── STEP 2: Extract recipes ───────────────────────────────────────
        print(f"STEP 2: Extract up to {max_results} recipes...")

        recipe_cards = page.locator(
            'a[data-doc-id]'
        )
        count = recipe_cards.count()
        print(f"  Found {count} recipe cards")

        for i in range(count):
            if len(results) >= max_results:
                break
            card = recipe_cards.nth(i)
            try:
                name = "N/A"
                rating = "N/A"
                cook_time = "N/A"

                # Recipe name
                try:
                    name_el = card.locator(
                        'span.card__title-text, '
                        'span[class*="title"], '
                        'h3, h4'
                    ).first
                    name = name_el.inner_text(timeout=2000).strip()
                except Exception:
                    try:
                        name = card.get_attribute("aria-label") or "N/A"
                    except Exception:
                        pass

                if name == "N/A":
                    continue

                # Click into recipe page to get rating and cook time
                checkpoint(f"Click recipe card: {name}")
                card.evaluate("el => el.click()")
                page.wait_for_timeout(2000)

                # Rating
                try:
                    rating_el = page.locator(
                        '#mm-recipes-review-bar__rating_1-0, '
                        '.mm-recipes-review-bar__rating'
                    ).first
                    rating_text = rating_el.inner_text(timeout=2000).strip()
                    rm = re.search(r"[\d.]+", rating_text)
                    if rm:
                        rating = rm.group(0)
                except Exception:
                    pass

                # Cook time — find the detail row containing "Total Time"
                try:
                    detail_items = page.locator('[class*="detail"]:has-text("Total Time")')
                    for j in range(detail_items.count()):
                        txt = detail_items.nth(j).inner_text(timeout=2000).strip()
                        tm = re.search(
                            r"Total Time[:\s]*(\d+\s*(?:hrs?|mins?|hours?|minutes?)[\s\d]*)",
                            txt, re.IGNORECASE,
                        )
                        if tm:
                            cook_time = tm.group(1).strip()
                            break
                except Exception:
                    pass

                results.append(AllrecipesRecipe(
                    name=name,
                    rating=rating,
                    cook_time=cook_time,
                ))
                print(f"  {len(results)}. {name} | Rating: {rating} | Time: {cook_time}")

                # Go back to search results
                checkpoint("Go back to search results")
                page.go_back()
                page.wait_for_timeout(2000)

            except Exception as e:
                print(f"  Error on card {i}: {e}")
                try:
                    page.go_back()
                    page.wait_for_timeout(2000)
                except Exception:
                    pass
                continue

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nFound {len(results)} recipes for '{query}':")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name}")
            print(f"     Rating: {r.rating}  Cook Time: {r.cook_time}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return AllrecipesSearchResult(
        query=query,
        recipes=results,
    )


def test_search_allrecipes() -> None:
    request = AllrecipesSearchRequest(
        query="chicken parmesan",
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
            result = search_allrecipes(page, request)
            assert result.query == request.query
            assert len(result.recipes) <= request.max_results
            print(f"\nTotal recipes found: {len(result.recipes)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_allrecipes)
