"""
USA.gov – Government Information Search
"""

import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class UsaGovSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class UsaGovSearchItem:
    title: str
    description: str
    url: str


@dataclass(frozen=True)
class UsaGovSearchResult:
    items: list  # list[UsaGovSearchItem]


# Searches USA.gov for government information matching the given query.
# Navigates to the search results page, waits for results to load,
# and extracts up to max_results items with title, description, and URL.
def usa_gov_search(page: Page, request: UsaGovSearchRequest) -> UsaGovSearchResult:
    query = request.query
    max_results = request.max_results
    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    results = []

    # ── Navigate directly to search results ──────────────────────────
    query_encoded = query.replace(" ", "+")
    search_url = f"https://search.usa.gov/search?affiliate=usagov_en_internal&query={query_encoded}"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to page")
    page.goto(search_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    # ── Wait for results ─────────────────────────────────────────────
    print("Waiting for results...")
    try:
        page.locator(".result").first.wait_for(state="visible", timeout=10000)
    except Exception:
        pass
    page.wait_for_timeout(1000)
    print(f"  Loaded: {page.url}")

    # ── Extract results ──────────────────────────────────────────────
    print(f"Extracting up to {max_results} results...")

    cards = page.locator(".result")
    count = cards.count()
    print(f"  Found {count} result cards on page")

    for i in range(min(count, max_results)):
        card = cards.nth(i)
        try:
            text = card.inner_text(timeout=3000)
            lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

            title = lines[0] if len(lines) > 0 else "N/A"
            description = lines[1] if len(lines) > 1 else "N/A"
            url = lines[2] if len(lines) > 2 else "N/A"
            if url != "N/A" and not url.startswith("http"):
                url = "https://" + url

            if title == "N/A":
                continue

            results.append(UsaGovSearchItem(
                title=title,
                description=description,
                url=url,
            ))
        except Exception:
            continue

    # ── Print results ─────────────────────────────────────────────────
    print(f'\nFound {len(results)} results for "{query}":\n')
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r.title}")
        print(f"     {r.description[:100]}")
        print(f"     {r.url}")
        print()

    return UsaGovSearchResult(items=results)


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    with sync_playwright() as p:
        chrome_user_data = os.path.join(
            os.environ["USERPROFILE"],
            "AppData", "Local", "Google", "Chrome", "User Data", "Default",
        )
        context = p.chromium.launch_persistent_context(
            chrome_user_data,
            headless=False,
            channel="chrome",
        )
        page = context.pages[0] if context.pages else context.new_page()
        request = UsaGovSearchRequest(query="passport renewal", max_results=5)
        result = usa_gov_search(page, request)
        print(f"\nTotal results found: {len(result.items)}")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
