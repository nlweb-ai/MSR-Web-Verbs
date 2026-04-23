"""
Auto-generated Playwright script (Python)
TripAdvisor – Things to Do
City: "Barcelona"

Generated on: 2026-04-18T02:36:47.939Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class TripAdvisorRequest:
    city: str = "Barcelona"
    city_slug: str = "Barcelona_Catalonia"
    geo_id: str = "g187497"
    max_attractions: int = 5


@dataclass
class Attraction:
    name: str = ""
    rating: str = ""
    num_reviews: str = ""
    category: str = ""


@dataclass
class TripAdvisorResult:
    attractions: list = field(default_factory=list)


def tripadvisor_things_to_do(page: Page, request: TripAdvisorRequest) -> TripAdvisorResult:
    """Extract top things to do from TripAdvisor."""
    print(f"  City: {request.city}\n")

    # ── Load page ─────────────────────────────────────────────────────
    url = f"https://www.tripadvisor.com/Attractions-{request.geo_id}-Activities-{request.city_slug}.html"
    print(f"Loading {url}...")
    checkpoint("Navigate to TripAdvisor")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)

    # Check for CAPTCHA
    body_len = page.evaluate("document.body.innerText.length")
    if body_len == 0:
        print("CAPTCHA detected. Retrying...")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(10000)

    # Scroll to load attractions
    for i in range(5):
        page.evaluate(f"window.scrollTo(0, {2000 * (i + 1)})")
        page.wait_for_timeout(500)
    page.wait_for_timeout(2000)

    # ── Extract attractions ───────────────────────────────────────────
    raw = page.evaluate(r"""(maxAttractions) => {
        const text = document.body.innerText;
        const idx = text.indexOf('\n1. ');
        if (idx === -1) return [];
        const section = text.substring(idx);
        const pattern = /(\d+)\.\s+(.+?)\n(\d\.\d)\n\(([0-9,]+)\)\n(.+?)\n/g;
        const results = [];
        let m;
        while ((m = pattern.exec(section)) && results.length < maxAttractions) {
            results.push({
                name: m[2].trim(),
                rating: m[3],
                num_reviews: m[4],
                category: m[5].trim(),
            });
        }
        return results;
    }""", request.max_attractions)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"TripAdvisor: Things to Do in {request.city}")
    print("=" * 60)
    for idx, a in enumerate(raw, 1):
        print(f"\n  {idx}. {a['name']}")
        print(f"     Rating: {a['rating']} ({a['num_reviews']} reviews)")
        print(f"     Category: {a['category']}")

    attractions = [Attraction(**a) for a in raw]
    return TripAdvisorResult(attractions=attractions)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("tripadvisor_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = tripadvisor_things_to_do(page, TripAdvisorRequest())
            print(f"\nReturned {len(result.attractions)} attractions")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
