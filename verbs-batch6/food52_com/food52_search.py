"""
Auto-generated Playwright script (Python)
Food52 – Recipe Search
Query: "sourdough bread"

Generated on: 2026-04-18T05:22:49.781Z
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
    query: str = "sourdough bread"
    max_results: int = 5


@dataclass
class Recipe:
    name: str = ""
    author: str = ""
    rating: str = ""
    description: str = ""


@dataclass
class RecipeResult:
    recipes: list = field(default_factory=list)


def food52_search(page: Page, request: RecipeRequest) -> RecipeResult:
    """Search Food52 for recipes."""
    print(f"  Query: {request.query}\n")

    # Navigate to Food52 and use the search box
    print("Loading https://food52.com/ ...")
    checkpoint("Navigate to Food52")
    page.goto("https://food52.com/", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # Click the search icon/button to reveal input
    checkpoint("Open search and type query")
    try:
        search_trigger = page.locator("button:has-text('Search'), a:has-text('Search'), [aria-label='Search'], [class*='search'] button, [class*='Search'] button").first
        search_trigger.click(timeout=5000)
        page.wait_for_timeout(1000)
    except Exception:
        pass

    # Find and fill the search input
    search_input = page.locator("input[type='search'], input[name='q'], input[placeholder*='search' i], input[placeholder*='Search']").first
    search_input.wait_for(state="visible", timeout=10000)
    search_input.fill(request.query)
    page.wait_for_timeout(500)
    page.keyboard.press("Enter")

    # Wait for search results page to load
    for attempt in range(10):
        page.wait_for_timeout(2000)
        body_text = page.evaluate("document.body.innerText") or ""
        if "404" not in body_text[:500] and len(body_text) > 1000:
            title = page.evaluate("document.title")
            print(f"  Poll {attempt+1}: page loaded, title={title}")
            break
        print(f"  Poll {attempt+1}: waiting...")

    # Scroll to trigger lazy-loaded content
    for _ in range(5):
        page.evaluate("window.scrollBy(0, 600)")
        page.wait_for_timeout(800)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    checkpoint("Extract recipe listings")

    items_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();

        // Strategy 1: find links to individual recipe pages (with numeric IDs)
        const links = document.querySelectorAll('a[href*="/recipes/"]');
        for (const a of links) {
            if (results.length >= maxResults) break;
            const href = a.getAttribute('href') || '';
            // Only want individual recipe links with numeric IDs like /recipes/12345-recipe-name
            if (!/\/recipes\/\d{4,}/.test(href)) continue;

            const block = a.closest('article, li, [class*="card"], [class*="recipe"], [class*="item"]') || a;
            const titleEl = block.querySelector('h2, h3, h4, [class*="title"], [class*="name"]');
            let name = titleEl ? titleEl.innerText.trim() : '';
            if (!name) name = (a.getAttribute('aria-label') || a.innerText || '').trim();
            name = name.split('\n')[0].trim();
            if (!name || name.length < 3 || seen.has(name)) continue;
            if (/^(menu|sign|log|search|home|shop|about|more|quick|one pot|gluten)/i.test(name)) continue;
            seen.add(name);

            const text = block.innerText || '';
            let author = '', rating = '', description = '';
            const authorEl = block.querySelector('[class*="author"], [class*="byline"], [class*="creator"]');
            if (authorEl) author = authorEl.innerText.trim().replace(/^by\s*/i, '');
            const ratM = text.match(/(\d+\.?\d*)\s*(?:\/\s*5|stars?|rating)/i);
            if (ratM) rating = ratM[1];
            const descEl = block.querySelector('p, [class*="desc"], [class*="dek"]');
            if (descEl) description = descEl.innerText.trim().slice(0, 200);

            results.push({ name: name.slice(0, 120), author, rating, description });
        }

        // Strategy 2: fallback — extract from page text
        if (results.length === 0) {
            const text = document.body.innerText;
            const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 10 && l.length < 150);
            for (const line of lines) {
                if (results.length >= maxResults) break;
                if (/sourdough|bread|recipe|bake/i.test(line) && !seen.has(line)) {
                    if (/^(menu|sign|log|search|home|shop|quick|one pot|gluten|filter)/i.test(line)) continue;
                    seen.add(line);
                    results.push({ name: line.slice(0, 120), author: '', rating: '', description: '' });
                }
            }
        }
        return results;
    }""", request.max_results)

    result = RecipeResult(recipes=[Recipe(**r) for r in items_data])

    print("\n" + "=" * 60)
    print(f"Food52: {request.query}")
    print("=" * 60)
    for r in result.recipes:
        print(f"  {r.name}")
        print(f"    Author: {r.author}  Rating: {r.rating}")
        print(f"    Desc: {r.description[:80]}...")
    print(f"\n  Total: {len(result.recipes)} recipes")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("food52_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = food52_search(page, RecipeRequest())
            print(f"\nReturned {len(result.recipes)} recipes")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
