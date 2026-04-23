import re
import os
from dataclasses import dataclass
from urllib.parse import quote as url_quote
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class SteamSearchRequest:
    search_term: str = "open world RPG"
    max_results: int = 5

@dataclass(frozen=True)
class SteamGame:
    title: str = ""
    price: str = ""
    release_date: str = ""
    review_summary: str = ""

@dataclass(frozen=True)
class SteamSearchResult:
    games: list = None  # list[SteamGame]

# Search Steam Store for PC games matching a search term
# and extract title, price, release date, and review summary.
def steam_search(page: Page, request: SteamSearchRequest) -> SteamSearchResult:
    search_term = request.search_term
    max_results = request.max_results
    print(f"  Search term: {search_term}")
    print(f"  Max results: {max_results}\n")

    search_url = f"https://store.steampowered.com/search/?term={url_quote(search_term)}"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to Steam search page")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    print(f"  Loaded: {page.url}")

    # Dismiss age gate / cookie banners
    for selector in [
        '#acceptAllButton',
        'button:has-text("Accept All")',
        '#agecheck_form button',
    ]:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=1000):
                checkpoint(f"Dismiss banner: {selector}")
                btn.click()
                page.wait_for_timeout(500)
                break
        except Exception:
            pass

    results = []

    # Extract games from search results
    checkpoint("Extract game listings from search results")
    game_rows = page.locator('a.search_result_row')
    count = game_rows.count()
    print(f"  Found {count} search result rows")

    for i in range(min(count, max_results)):
        row = game_rows.nth(i)
        try:
            # Title
            title = "N/A"
            try:
                t_el = row.locator('span.title').first
                title = t_el.inner_text(timeout=2000).strip()
            except Exception:
                pass
            if title == "N/A":
                continue

            # Price
            price = "N/A"
            try:
                disc_el = row.locator('.discount_final_price, .search_price')
                p_text = disc_el.first.inner_text(timeout=2000).strip()
                p_m = re.search(r'(\$[\d,.]+|Free|Free to Play)', p_text, re.IGNORECASE)
                if p_m:
                    price = p_m.group(1)
                elif "free" in p_text.lower():
                    price = "Free"
            except Exception:
                pass

            # Release date
            release_date = "N/A"
            try:
                d_el = row.locator('.search_released').first
                release_date = d_el.inner_text(timeout=2000).strip()
            except Exception:
                pass

            # Review summary
            review_summary = "N/A"
            try:
                r_el = row.locator('.search_review_summary').first
                review_summary = r_el.get_attribute("data-tooltip-html", timeout=2000) or "N/A"
                m = re.search(r'(Overwhelmingly Positive|Very Positive|Positive|Mostly Positive|Mixed|Mostly Negative|Negative|Very Negative|Overwhelmingly Negative)', review_summary, re.IGNORECASE)
                if m:
                    review_summary = m.group(1)
                else:
                    review_summary = review_summary.split("<br>")[0].strip()
            except Exception:
                pass

            results.append(SteamGame(
                title=title,
                price=price,
                release_date=release_date,
                review_summary=review_summary,
            ))
        except Exception:
            continue

    print("=" * 60)
    print(f"Steam Store - Search Results for \"{search_term}\"")
    print("=" * 60)
    for idx, g in enumerate(results, 1):
        print(f"\n{idx}. {g.title}")
        print(f"   Price: {g.price}")
        print(f"   Released: {g.release_date}")
        print(f"   Reviews: {g.review_summary}")

    print(f"\nFound {len(results)} games")

    return SteamSearchResult(games=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = steam_search(page, SteamSearchRequest())
        print(f"\nReturned {len(result.games or [])} games")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
