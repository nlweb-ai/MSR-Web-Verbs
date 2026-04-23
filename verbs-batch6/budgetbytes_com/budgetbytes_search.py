"""
Auto-generated Playwright script (Python)
Budget Bytes – Recipe Search
Query: "meal prep"

Generated on: 2026-04-18T05:00:12.101Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class RecipeRequest:
    query: str = "meal prep"
    max_recipes: int = 5


@dataclass
class Recipe:
    name: str = ""
    cost_per_serving: str = ""
    prep_time: str = ""
    cook_time: str = ""
    servings: str = ""


@dataclass
class RecipeResult:
    recipes: list = field(default_factory=list)


def budgetbytes_search(page: Page, request: RecipeRequest) -> RecipeResult:
    """Search Budget Bytes for recipes."""
    print(f"  Query: {request.query}\n")

    url = f"https://www.budgetbytes.com/?s={quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Budget Bytes search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract recipe listings")
    recipes_data = page.evaluate(r"""(maxRecipes) => {
        const results = [];
        const cards = document.querySelectorAll(
            'article, .post, [class*="recipe"], .archive-post'
        );
        const seen = new Set();
        for (const card of cards) {
            if (results.length >= maxRecipes) break;
            const titleEl = card.querySelector('h2, h3, h4, .entry-title, [class*="title"]');
            const name = titleEl ? titleEl.innerText.trim() : '';
            if (!name || name.length < 5 || seen.has(name)) continue;
            seen.add(name);

            const text = card.innerText || '';
            let cost_per_serving = '', prep_time = '', cook_time = '', servings = '';

            const costM = text.match(/\$(\d+\.\d{2})\s*(?:per serving|\/serving)/i);
            if (costM) cost_per_serving = costM[0];

            const prepM = text.match(/(?:Prep|Preparation)\s*(?:Time)?[:\s]*(\d+\s*(?:min|hour|hr))/i);
            if (prepM) prep_time = prepM[1];

            const cookM = text.match(/(?:Cook|Cooking)\s*(?:Time)?[:\s]*(\d+\s*(?:min|hour|hr))/i);
            if (cookM) cook_time = cookM[1];

            const servM = text.match(/(\d+)\s*(?:serving|portion)/i);
            if (servM) servings = servM[1];

            results.push({ name, cost_per_serving, prep_time, cook_time, servings });
        }
        return results;
    }""", request.max_recipes)

    result = RecipeResult(recipes=[Recipe(**r) for r in recipes_data])

    print("\n" + "=" * 60)
    print(f"Budget Bytes: {request.query}")
    print("=" * 60)
    for r in result.recipes:
        print(f"  {r.name}")
        print(f"    Cost: {r.cost_per_serving}  Prep: {r.prep_time}  Cook: {r.cook_time}  Servings: {r.servings}")
    print(f"\n  Total: {len(result.recipes)} recipes")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("budgetbytes_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = budgetbytes_search(page, RecipeRequest())
            print(f"\nReturned {len(result.recipes)} recipes")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
