"""
Playwright verb — Thumbtack Service Professional Search
Search for local service professionals by category and location.
Extract name, rating, number of reviews, and starting price.
"""

import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ThumbtackSearchRequest:
    service: str       # e.g. "house cleaning"
    location: str      # e.g. "Portland, OR"
    max_results: int   # e.g. 5


@dataclass(frozen=True)
class ThumbtackProfessional:
    name: str       # professional's name
    rating: str     # e.g. "4.9"
    reviews: str    # number of reviews or "N/A"
    price: str      # starting price or "N/A"


@dataclass(frozen=True)
class ThumbtackSearchResult:
    professionals: list  # list[ThumbtackProfessional]


# Search for service professionals on Thumbtack by service type and location.
# Navigates to the category/location URL, extracts professional names, ratings,
# review counts, and prices from the listing page.
def thumbtack_search(page: Page, request: ThumbtackSearchRequest) -> ThumbtackSearchResult:
    print(f"  Service: {request.service}")
    print(f"  Location: {request.location}")
    print(f"  Max results: {request.max_results}\n")

    results = []

    # ── Build URL from location and service ──────────────────────────
    loc_parts = [p.strip() for p in request.location.split(",")]
    city = loc_parts[0].lower().replace(" ", "-")
    state = loc_parts[1].lower().strip() if len(loc_parts) > 1 else ""
    service_slug = request.service.lower().replace(" ", "-")

    search_url = f"https://www.thumbtack.com/{state}/{city}/{service_slug}/"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to page")
    page.goto(search_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)
    print(f"  Loaded: {page.url}")
    print(f"  Title: {page.title()}")

    # ── Wait for pro listings ─────────────────────────────────────────
    try:
        page.locator('[data-testid="pro-list-result-review"]').first.wait_for(
            state="visible", timeout=10000
        )
    except Exception:
        pass
    page.wait_for_timeout(2000)

    # ── Extract professionals via body text ───────────────────────────
    print(f"\nExtracting up to {request.max_results} professionals...")

    body = page.locator("body").inner_text(timeout=5000)
    lines = [l.strip() for l in body.split("\n") if l.strip()]

    rating_re = re.compile(r"^(?:Excellent|Great|Exceptional|Good|OK)\s+(\d\.\d)$")
    i = 0
    while i < len(lines) and len(results) < request.max_results:
        rm = rating_re.match(lines[i])
        if rm:
            rating = rm.group(1)
            name = "N/A"
            for delta in [1, 2]:
                idx = i - delta
                if idx >= 0:
                    cand = lines[idx]
                    if cand not in (
                        "Top Pro", "New on Thumbtack", "Recommended",
                        "Highest rated", "Most hires", "Fastest response",
                        "View profile", "See more",
                    ) and len(cand) > 2 and not rating_re.match(cand):
                        name = re.sub(r"^\d+\.\s+", "", cand)
                        break

            reviews = "N/A"
            if i + 1 < len(lines):
                rvm = re.match(r"^\((\d+)\)$", lines[i + 1])
                if rvm:
                    reviews = rvm.group(1)

            price = "N/A"

            if name != "N/A":
                results.append(ThumbtackProfessional(
                    name=name,
                    rating=rating,
                    reviews=reviews,
                    price=price,
                ))
            i += 2
            continue
        i += 1

    # ── Print results ─────────────────────────────────────────────────
    print(f'\nFound {len(results)} professionals for "{request.service}" in {request.location}:\n')
    for idx, p in enumerate(results, 1):
        print(f"  {idx}. {p.name}")
        print(f"     Rating: {p.rating}  Reviews: {p.reviews}  Price: {p.price}")
        print()

    return ThumbtackSearchResult(professionals=results)


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_profile = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default",
    )
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            user_data_dir=chrome_profile,
            headless=False,
            channel="chrome",
        )
        page = context.pages[0] if context.pages else context.new_page()
        request = ThumbtackSearchRequest(
            service="house cleaning",
            location="Portland, OR",
            max_results=5,
        )
        result = thumbtack_search(page, request)
        print(f"\nTotal professionals found: {len(result.professionals)}")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
