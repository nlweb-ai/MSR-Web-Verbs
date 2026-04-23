"""Playwright script (Python) — Smitten Kitchen"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class SmittenKitchenRequest:
    tag: str = "vegetarian"
    max_results: int = 5

@dataclass
class RecipeItem:
    name: str = ""
    publish_date: str = ""

@dataclass
class SmittenKitchenResult:
    recipes: List[RecipeItem] = field(default_factory=list)

def search_smittenkitchen(page: Page, request: SmittenKitchenRequest) -> SmittenKitchenResult:
    url = f"https://smittenkitchen.com/tag/{request.tag}/"
    checkpoint("Navigate to Smitten Kitchen")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    result = SmittenKitchenResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: "RECIPE" marker, then recipe name, then "DATE JUMP TO COMMENTS"
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'RECIPE' && i + 2 < lines.length) {
                const name = lines[i + 1];
                const dateLine = lines[i + 2];
                const publish_date = dateLine.replace(/\\s*JUMP TO COMMENTS.*$/, '');
                if (name.length > 3) {
                    results.push({ name, publish_date });
                }
                i += 2;
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = RecipeItem()
        item.name = d.get("name", "")
        item.publish_date = d.get("publish_date", "")
        result.recipes.append(item)

    print(f"\nFound {len(result.recipes)} recipes:")
    for i, r in enumerate(result.recipes, 1):
        print(f"  {i}. {r.name} ({r.publish_date})")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("smittenkitchen")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_smittenkitchen(page, SmittenKitchenRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
