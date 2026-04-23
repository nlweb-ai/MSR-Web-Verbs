"""
Playwright script (Python) — Clutch Agency Search
Search for top agencies on Clutch.co.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ClutchSearchRequest:
    service: str = "web development"
    max_results: int = 5


@dataclass
class AgencyItem:
    name: str = ""
    location: str = ""
    min_project_size: str = ""
    hourly_rate: str = ""
    rating: str = ""
    num_reviews: str = ""


@dataclass
class ClutchSearchResult:
    service: str = ""
    items: List[AgencyItem] = field(default_factory=list)


def search_clutch(page: Page, request: ClutchSearchRequest) -> ClutchSearchResult:
    """Search Clutch.co for top agencies."""
    slug = request.service.replace(" ", "-").lower()
    # Map common services to Clutch URL paths
    service_map = {"web development": "web-developers", "mobile app development": "app-developers",
                   "seo": "seo-firms", "digital marketing": "digital-marketing"}
    path_slug = service_map.get(request.service.lower(), slug)
    url = f"https://clutch.co/{path_slug}"
    print(f"Loading {url}...")
    checkpoint("Navigate to agency listing")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = ClutchSearchResult(service=request.service)

    checkpoint("Extract agencies")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('[class*="provider"], [class*="company"], [data-content*="provider"], li[class*="provider"]');
        for (const card of cards) {
            if (items.length >= max) break;
            const text = (card.textContent || '').replace(/\\s+/g, ' ').trim();

            let name = '';
            const nameEl = card.querySelector('h3 a, h2 a, [class*="company-name"], [class*="title"] a');
            if (nameEl) name = nameEl.textContent.trim();
            if (!name || name.length < 2 || name.length > 200) continue;
            if (items.some(i => i.name === name)) continue;

            let location = '';
            const locEl = card.querySelector('[class*="location"], [class*="locality"]');
            if (locEl) location = locEl.textContent.trim();

            let minProject = '';
            const projMatch = text.match(/(?:Min(?:imum)?\\s*)?(?:Project\\s*(?:Size)?)?:?\\s*\\$[\\d,]+\\+?/i);
            if (projMatch) minProject = projMatch[0].replace(/.*?\\$/, '$');

            let hourly = '';
            const hrMatch = text.match(/\\$[\\d,]+\\s*-\\s*\\$[\\d,]+\\s*\\/\\s*hr/i);
            if (hrMatch) hourly = hrMatch[0];

            let rating = '';
            const ratingMatch = text.match(/(\\d+\\.\\d+)\\s*/);
            if (ratingMatch) rating = ratingMatch[1];

            let reviews = '';
            const revMatch = text.match(/(\\d+)\\s*(?:review|verified)/i);
            if (revMatch) reviews = revMatch[1];

            items.push({name: name, location: location, min_project_size: minProject, hourly_rate: hourly, rating: rating, num_reviews: reviews});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = AgencyItem()
        item.name = d.get("name", "")
        item.location = d.get("location", "")
        item.min_project_size = d.get("min_project_size", "")
        item.hourly_rate = d.get("hourly_rate", "")
        item.rating = d.get("rating", "")
        item.num_reviews = d.get("num_reviews", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} agencies for '{request.service}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name}")
        print(f"     Location: {item.location}  Min: {item.min_project_size}  Rate: {item.hourly_rate}  Rating: {item.rating}  Reviews: {item.num_reviews}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("clutch")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_clutch(page, ClutchSearchRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} agencies")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
