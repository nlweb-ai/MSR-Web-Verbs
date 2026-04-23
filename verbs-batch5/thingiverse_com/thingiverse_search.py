"""
Auto-generated Playwright script (Python)
Thingiverse – Search 3D Models
Query: "phone stand"

Generated on: 2026-04-18T02:27:15.001Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
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
class ThingiverseRequest:
    query: str = "phone stand"
    max_models: int = 5


@dataclass
class ThingiverseModel:
    name: str = ""
    creator: str = ""
    likes: str = ""
    url: str = ""


@dataclass
class ThingiverseResult:
    models: list = field(default_factory=list)


def thingiverse_search(page: Page, request: ThingiverseRequest) -> ThingiverseResult:
    """Search thingiverse.com for 3D models."""
    print(f"  Query: {request.query}\n")

    # ── Search ────────────────────────────────────────────────────────
    search_url = f"https://www.thingiverse.com/search?q={quote_plus(request.query)}&type=things"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to Thingiverse search")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    # ── Extract models ────────────────────────────────────────────────
    raw_models = page.evaluate(r"""(maxModels) => {
        const cards = document.querySelectorAll('[class*="ThingCard"]');
        const results = [];
        for (const card of cards) {
            if (results.length >= maxModels) break;
            // Skip ads
            if (card.innerText.includes('Ad')) continue;
            const link = card.querySelector('a[href*="/thing:"]');
            if (!link) continue;
            const url = link.href;
            const lines = card.innerText.trim().split('\n').filter(l => l.trim());
            // Pattern: model_name, likes_count, creator
            if (lines.length >= 3) {
                results.push({
                    name: lines[0],
                    likes: lines[1],
                    creator: lines[2],
                    url: url,
                });
            }
        }
        return results;
    }""", request.max_models)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Thingiverse: {request.query}")
    print("=" * 60)
    for idx, m in enumerate(raw_models, 1):
        print(f"\n  {idx}. {m['name']}")
        print(f"     Creator: {m['creator']}")
        print(f"     Likes: {m['likes']}")
        print(f"     URL: {m['url']}")

    models = [ThingiverseModel(**m) for m in raw_models]
    return ThingiverseResult(models=models)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("thingiverse_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = thingiverse_search(page, ThingiverseRequest())
            print(f"\nReturned {len(result.models)} models")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
