"""
Auto-generated Playwright script (Python)
Good On You – Brand Rating
Brand: "Patagonia"

Generated on: 2026-04-18T05:29:58.646Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BrandRequest:
    brand: str = "Patagonia"


@dataclass
class BrandResult:
    name: str = ""
    overall_rating: str = ""
    planet_score: str = ""
    people_score: str = ""
    animals_score: str = ""
    summary: str = ""


def goodonyou_search(page: Page, request: BrandRequest) -> BrandResult:
    """Look up brand rating on Good On You."""
    print(f"  Brand: {request.brand}\n")

    # Try the directory search page first
    url = f"https://directory.goodonyou.eco/brand/{request.brand.lower().replace(' ', '-')}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Good On You brand page")
    page.goto(url, wait_until="domcontentloaded")

    # Wait for content to render (CSR)
    for attempt in range(8):
        page.wait_for_timeout(2000)
        body_len = page.evaluate("document.body.innerText.length")
        print(f"  Poll {attempt+1}: bodyLen={body_len}")
        if body_len > 1000:
            break

    # Scroll page
    for _ in range(3):
        page.evaluate("window.scrollBy(0, 400)")
        page.wait_for_timeout(600)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(500)

    checkpoint("Extract brand rating data")
    # Use page.evaluate for more reliable extraction
    rating_data = page.evaluate(r"""() => {
        const text = document.body.innerText;
        const result = { name: '', overall: '', planet: '', people: '', animals: '', summary: '' };

        const h1 = document.querySelector('h1');
        if (h1) result.name = h1.innerText.trim();

        // Look for "RATED: Good" or similar
        const ratedM = text.match(/RATED:\s*(\w+)/i);
        if (ratedM) result.overall = ratedM[1].trim();

        // Look for category scores — "Planet" / "People" / "Animals" followed by a rating
        // These are usually displayed as: "Planet\n4" or "Planet\nGood" etc.
        const lines = text.split('\n').map(l => l.trim());
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].toLowerCase();
            const nextLine = i + 1 < lines.length ? lines[i + 1].trim() : '';
            if (line === 'planet' || line === 'environment') result.planet = nextLine;
            if (line === 'people' || line === 'labour' || line === 'workers') result.people = nextLine;
            if (line === 'animals' || line === 'animal') result.animals = nextLine;
        }

        // Summary from meta description or first paragraph
        const metaDesc = document.querySelector('meta[name="description"]');
        if (metaDesc) result.summary = (metaDesc.getAttribute('content') || '').slice(0, 300);

        return result;
    }""")

    result = BrandResult(
        name=rating_data.get('name') or request.brand,
        overall_rating=rating_data.get('overall', ''),
        planet_score=rating_data.get('planet', ''),
        people_score=rating_data.get('people', ''),
        animals_score=rating_data.get('animals', ''),
        summary=rating_data.get('summary', ''),
    )

    print("\n" + "=" * 60)
    print(f"Good On You: {result.name}")
    print("=" * 60)
    print(f"  Overall Rating: {result.overall_rating}")
    print(f"  Planet:         {result.planet_score}")
    print(f"  People:         {result.people_score}")
    print(f"  Animals:        {result.animals_score}")
    print(f"  Summary:        {result.summary[:80]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("goodonyou_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = goodonyou_search(page, BrandRequest())
            print(f"\nReturned info for {result.name}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
