"""
Auto-generated Playwright script (Python)
Liquor.com – Search cocktail recipes

Uses CDP-launched Chrome to avoid bot detection.
Search → collect recipe links → visit each → extract name + ingredients.
"""

import os, sys, shutil, urllib.parse
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CocktailSearchRequest:
    query: str = "margarita"
    max_results: int = 3


@dataclass
class Cocktail:
    name: str = ""
    ingredients: List[str] = field(default_factory=list)


@dataclass
class CocktailSearchResult:
    cocktails: List[Cocktail] = field(default_factory=list)


def cocktail_search(page: Page, request: CocktailSearchRequest) -> CocktailSearchResult:
    """Search Liquor.com for cocktail recipes and extract details."""
    print(f"  Query: {request.query}")
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Search Liquor.com")
    q = urllib.parse.quote_plus(request.query)
    page.goto(f"https://www.liquor.com/search?q={q}", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Collect recipe URLs")
    urls = page.evaluate(
        r"""(max) => {
            const links = document.querySelectorAll('a[href*="/recipes/"]');
            const seen = new Set();
            const results = [];
            for (const a of links) {
                if (results.length >= max) break;
                const href = a.href;
                if (seen.has(href)) continue;
                seen.add(href);
                results.push(href);
            }
            return results;
        }""",
        request.max_results,
    )

    result = CocktailSearchResult()

    for i, url in enumerate(urls):
        checkpoint(f"Visit recipe {i + 1}")
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        info = page.evaluate(r"""() => {
            const h1 = document.querySelector('h1');
            const name = h1 ? h1.textContent.trim() : '';

            const ingredientEls = document.querySelectorAll('[class*="ingredient"] li, [class*="ingredient-list"] li');
            const ingredients = [];
            for (const el of ingredientEls) {
                const text = el.textContent.trim();
                if (text && !text.startsWith('Garnish:')) ingredients.push(text);
            }

            // Fallback: parse from innerText
            if (ingredients.length === 0) {
                const body = document.body.innerText;
                const match = body.match(/Ingredients\s*\n([\s\S]+?)(?:Steps|Directions|Instructions)/);
                if (match) {
                    const lines = match[1].split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('Garnish'));
                    ingredients.push(...lines);
                }
            }

            return {name, ingredients};
        }""")

        c = Cocktail()
        c.name = info.get("name", "")
        c.ingredients = info.get("ingredients", [])
        result.cocktails.append(c)

    for i, c in enumerate(result.cocktails):
        print(f"  Cocktail {i + 1}: {c.name}")
        for ing in c.ingredients:
            print(f"    - {ing}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("liquor")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = CocktailSearchRequest()
            result = cocktail_search(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.cocktails)} cocktails")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
