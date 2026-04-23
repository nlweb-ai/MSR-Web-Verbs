"""
Playwright verb — TripAdvisor Restaurant Search
Search for restaurants by city and extract name, cuisine, rating, and price level.
Uses Google redirect to bypass TripAdvisor challenge pages.
"""

import re
import os
import urllib.parse
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class TripadvisorRestaurantSearchRequest:
    destination: str          # city to search (e.g. "New Orleans, LA")
    max_results: int = 5      # maximum number of restaurants to return


@dataclass(frozen=True)
class RestaurantInfo:
    name: str
    cuisine: str
    rating: str
    price_level: str


@dataclass(frozen=True)
class TripadvisorRestaurantSearchResult:
    restaurants: list  # list[RestaurantInfo]


# Search for restaurants in a given city on TripAdvisor via Google redirect,
# extracting name, cuisine type, rating, and price level for each result.
def tripadvisor_restaurant_search(page: Page, request: TripadvisorRestaurantSearchRequest) -> TripadvisorRestaurantSearchResult:
    print(f"  Destination: {request.destination}")
    print(f"  Max results: {request.max_results}\n")

    results = []

    # ── Navigate via Google redirect ──────────────────────────────────
    google_q = urllib.parse.quote(f"site:tripadvisor.com Restaurants {request.destination}")
    google_url = f"https://www.google.com/search?q={google_q}"
    print(f"Loading Google: {google_url}...")
    checkpoint("Navigate to page")
    page.goto(google_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    # Find the TripAdvisor restaurants link
    links = page.locator('a[href*="tripadvisor.com/Restaurants-"]')
    lc = links.count()
    print(f"  Found {lc} TripAdvisor restaurant links")

    if lc == 0:
        print("  No TripAdvisor links found on Google. Aborting.")
        return TripadvisorRestaurantSearchResult(restaurants=[])

    href = links.first.get_attribute("href", timeout=5000)
    print(f"  Navigating to TripAdvisor...")
    checkpoint("Navigate to page")
    page.goto(href, timeout=30000)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    # Handle challenge page (title == "tripadvisor.com")
    if page.title() == "tripadvisor.com":
        print("  Challenge page detected, reloading...")
        checkpoint("Wait for page")
        page.reload()
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

    print(f"  Loaded: {page.title()}")
    print(f"  URL: {page.url}")

    # ── Extract restaurants via body text parsing ─────────────────────
    print(f"\nExtracting up to {request.max_results} restaurants...")

    body = page.locator("body").inner_text(timeout=5000)
    lines = [l.strip() for l in body.split("\n") if l.strip()]

    i = 0
    while i < len(lines) and len(results) < request.max_results:
        m = re.match(r"^\d+\.\s+(.+)$", lines[i])
        if m:
            name = m.group(1).strip()
            if i + 1 < len(lines) and re.match(r"^\d\.\d$", lines[i + 1]):
                rating = lines[i + 1]
                reviews = ""
                if i + 2 < len(lines) and "review" in lines[i + 2].lower():
                    reviews = lines[i + 2]
                cuisine = "N/A"
                if i + 3 < len(lines):
                    cand = lines[i + 3]
                    if not cand.startswith("$") and not re.match(r"^\d", cand):
                        cuisine = cand
                price_level = "N/A"
                if i + 4 < len(lines):
                    cand = lines[i + 4]
                    if re.match(r"^\$", cand):
                        price_level = cand
                if cuisine != "N/A" and " • " in cuisine:
                    parts = cuisine.split(" • ", 1)
                    cuisine = parts[0].strip()
                    price_level = parts[1].strip()

                results.append(RestaurantInfo(
                    name=name,
                    cuisine=cuisine,
                    rating=rating,
                    price_level=price_level,
                ))
                i += 5
                continue
        i += 1

    # ── Print results ─────────────────────────────────────────────────
    print(f'\nFound {len(results)} restaurants in "{request.destination}":\n')
    for idx, r in enumerate(results, 1):
        print(f"  {idx}. {r.name}")
        print(f"     Cuisine: {r.cuisine}  Rating: {r.rating}  Price: {r.price_level}")
        print()

    return TripadvisorRestaurantSearchResult(restaurants=results)


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    with sync_playwright() as p:
        chrome_profile = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default")
        context = p.chromium.launch_persistent_context(chrome_profile, headless=False, channel="chrome")
        page = context.pages[0] if context.pages else context.new_page()
        req = TripadvisorRestaurantSearchRequest(destination="New Orleans, LA", max_results=5)
        result = tripadvisor_restaurant_search(page, req)
        print(f"\nTotal restaurants found: {len(result.restaurants)}")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
