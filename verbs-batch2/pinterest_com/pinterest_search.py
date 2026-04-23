"""
Playwright script (Python) — Pinterest Pin Search
Search for pins and extract title and link.

Uses the user's Chrome profile for persistent login state.
"""

import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class PinterestSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class PinterestPin:
    title: str
    link: str


@dataclass(frozen=True)
class PinterestSearchResult:
    query: str
    pins: list[PinterestPin]


# Searches Pinterest for pins matching a query, then extracts
# up to max_results pins with title and link.
def search_pinterest(
    page: Page,
    request: PinterestSearchRequest,
) -> PinterestSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}\n")

    results: list[PinterestPin] = []

    try:
        url = f"https://www.pinterest.com/search/pins/?q={query.replace(' ', '+')}"
        checkpoint(f"Navigate to {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        for sel in ["button:has-text('Accept')", "button:has-text('Close')", "button:has-text('Not now')"]:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {sel}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        cards = page.locator('[data-test-id="pin"]')
        count = cards.count()
        seen_links = set()

        for i in range(count):
            if len(results) >= max_results:
                break
            card = cards.nth(i)
            title = link = "N/A"
            try:
                link_el = card.locator('a[href*="/pin/"]').first
                link = link_el.get_attribute("href", timeout=3000) or "N/A"
            except Exception:
                pass
            if link in seen_links:
                continue
            seen_links.add(link)
            try:
                al = card.locator('a[aria-label]').first.get_attribute("aria-label", timeout=3000) or ""
                if al:
                    title = al
            except Exception:
                pass
            if title == "N/A":
                try:
                    title = card.locator('img[alt]').first.get_attribute("alt", timeout=3000) or "N/A"
                except Exception:
                    pass
            if title != "N/A":
                results.append(PinterestPin(title=title[:100], link=link))
                print(f"  {len(results)}. {title[:80]} | {link}")

        print(f"\nFound {len(results)} pins:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.title}\n     {r.link}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return PinterestSearchResult(query=query, pins=results)


def test_search_pinterest() -> None:
    request = PinterestSearchRequest(query="minimalist home office", max_results=5)
    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir, channel="chrome", headless=False, viewport=None,
            args=["--disable-blink-features=AutomationControlled", "--disable-infobars", "--disable-extensions"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_pinterest(page, request)
            assert result.query == request.query
            assert len(result.pins) <= request.max_results
            print(f"\nTotal pins found: {len(result.pins)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_pinterest)
