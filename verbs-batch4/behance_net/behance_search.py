"""
Auto-generated Playwright script (Python)
Behance – Creative Project Search
Search for creative projects and extract project details.

Generated on: 2026-04-16T21:12:03.796Z
Recorded 1 browser interactions
"""

import re
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class BehanceSearchRequest:
    search_query: str = "brand identity"
    max_results: int = 5

@dataclass(frozen=True)
class BehanceProject:
    title: str = ""
    creator: str = ""
    appreciations: str = ""
    views: str = ""

@dataclass(frozen=True)
class BehanceSearchResult:
    projects: list = None  # list[BehanceProject]

def behance_search(page: Page, request: BehanceSearchRequest) -> BehanceSearchResult:
    query = request.search_query
    max_results = request.max_results
    print(f"  Search query: {query}")
    print(f"  Max results: {max_results}\n")

    url = f"https://www.behance.net/search/projects?search={quote_plus(query)}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to {url}")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    results = []

    # Each project is a div[class*="ProjectCover-root"] containing:
    #   - a[aria-label="title"] for title + URL
    #   - [class*="Owners"] for creator name
    #   - [class*="Stats"] for appreciations/views text
    cards = page.locator('div[class*="ProjectCover-root"]')
    count = cards.count()
    print(f"  Found {count} project cards")

    for i in range(min(count, max_results)):
        card = cards.nth(i)
        try:
            title = "N/A"
            creator = "N/A"
            appreciations = "N/A"
            views = "N/A"

            title_el = card.locator('a[aria-label="title"]')
            if title_el.count() > 0:
                title = title_el.first.inner_text(timeout=3000).strip()

            owner_el = card.locator('[class*="Owners"]')
            if owner_el.count() > 0:
                creator = owner_el.first.inner_text(timeout=3000).strip()

            stats_el = card.locator('[class*="Stats"]')
            if stats_el.count() > 0:
                stats_text = stats_el.first.inner_text(timeout=3000).strip()
                # Stats text looks like: "8K\n7,996 appreciations for ...\n94.2K\n94,231 views for ..."
                appr_m = re.search(r'([\d,]+)\s+appreciations', stats_text)
                views_m = re.search(r'([\d,]+)\s+views', stats_text)
                if appr_m:
                    appreciations = appr_m.group(1)
                if views_m:
                    views = views_m.group(1)

            if title != "N/A":
                results.append(BehanceProject(
                    title=title,
                    creator=creator,
                    appreciations=appreciations,
                    views=views,
                ))
        except Exception:
            continue

    print("=" * 60)
    print(f'Behance - Search Results for "{query}"')
    print("=" * 60)
    for idx, p in enumerate(results, 1):
        print(f"\n{idx}. {p.title}")
        print(f"   Creator: {p.creator}")
        print(f"   Appreciations: {p.appreciations}")
        print(f"   Views: {p.views}")

    print(f"\nFound {len(results)} projects")

    return BehanceSearchResult(projects=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = behance_search(page, BehanceSearchRequest())
        print(f"\nReturned {len(result.projects or [])} projects")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
