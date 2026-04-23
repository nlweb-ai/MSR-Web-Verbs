"""
Auto-generated Playwright script (Python)
DogTime – Search for dog breed information
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class DogtimeSearchRequest:
    search_query: str = "golden retriever"
    max_results: int = 5


@dataclass
class DogtimeBreedItem:
    breed_name: str = ""
    size: str = ""
    energy_level: str = ""
    grooming_needs: str = ""
    good_with_kids: str = ""
    description: str = ""


@dataclass
class DogtimeSearchResult:
    items: List[DogtimeBreedItem] = field(default_factory=list)


# Search for dog breed information on DogTime.
def dogtime_search(page: Page, request: DogtimeSearchRequest) -> DogtimeSearchResult:
    """Search for dog breed information on DogTime."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://dogtime.com/?s={query}"
    print(f"Loading {url}...")
    checkpoint("Navigate to DogTime search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = DogtimeSearchResult()

    checkpoint("Extract breed listings")
    js_code = """(max) => {
        const cards = document.querySelectorAll('article, [class*="post"], [class*="result"], [class*="entry"], [class*="card"], [class*="breed"]');
        const items = [];
        for (const card of cards) {
            if (items.length >= max) break;
            const nameEl = card.querySelector('h2 a, h3 a, h2, h3, [class*="title"] a, [class*="name"]');
            const sizeEl = card.querySelector('[class*="size"], [class*="weight"]');
            const energyEl = card.querySelector('[class*="energy"], [class*="activity"]');
            const groomEl = card.querySelector('[class*="groom"], [class*="maintenance"]');
            const kidsEl = card.querySelector('[class*="kids"], [class*="family"], [class*="children"]');
            const descEl = card.querySelector('p, [class*="excerpt"], [class*="description"], [class*="summary"]');

            const breed_name = nameEl ? nameEl.textContent.trim() : '';
            const size = sizeEl ? sizeEl.textContent.trim() : '';
            const energy_level = energyEl ? energyEl.textContent.trim() : '';
            const grooming_needs = groomEl ? groomEl.textContent.trim() : '';
            const good_with_kids = kidsEl ? kidsEl.textContent.trim() : '';
            const description = descEl ? descEl.textContent.trim() : '';

            if (breed_name) {
                items.push({breed_name, size, energy_level, grooming_needs, good_with_kids, description});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = DogtimeBreedItem()
        item.breed_name = d.get("breed_name", "")
        item.size = d.get("size", "")
        item.energy_level = d.get("energy_level", "")
        item.grooming_needs = d.get("grooming_needs", "")
        item.good_with_kids = d.get("good_with_kids", "")
        item.description = d.get("description", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Result {i}:")
        print(f"    Breed:      {item.breed_name}")
        print(f"    Size:       {item.size}")
        print(f"    Energy:     {item.energy_level}")
        print(f"    Grooming:   {item.grooming_needs}")
        print(f"    Kids:       {item.good_with_kids}")
        print(f"    Desc:       {item.description[:80]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("dogtime")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = DogtimeSearchRequest()
            result = dogtime_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} results")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
