"""
Playwright script (Python) — Medium Article Search
Search for articles and extract title, author, and date.

Uses the user's Chrome profile for persistent login state.
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
class MediumSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class MediumArticle:
    title: str
    author: str
    date: str


@dataclass(frozen=True)
class MediumSearchResult:
    query: str
    articles: list[MediumArticle]


# Searches Medium for articles matching a query, then extracts
# up to max_results articles with title, author, and date.
def search_medium(
    page: Page,
    request: MediumSearchRequest,
) -> MediumSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}\n")

    results: list[MediumArticle] = []

    try:
        url = f"https://medium.com/search?q={query.replace(' ', '+')}"
        checkpoint(f"Navigate to {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        for sel in ["button:has-text('Accept')", "button:has-text('Got it')", "button:has-text('Close')"]:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {sel}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        cards = page.locator('article')
        count = cards.count()

        for i in range(min(count, max_results)):
            card = cards.nth(i)
            title = author = date = "N/A"
            try:
                title = card.locator('h2, h3').first.inner_text(timeout=2000).strip()
            except Exception:
                pass
            try:
                author = card.locator('a[href*="@"]').first.inner_text(timeout=2000).strip()
            except Exception:
                pass
            try:
                card_text = card.inner_text(timeout=2000)
                dm = re.search(r"(\d+[dhm]\s+ago|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+)", card_text)
                date = dm.group(1) if dm else "N/A"
            except Exception:
                pass
            if title != "N/A":
                results.append(MediumArticle(title=title, author=author, date=date))
                print(f"  {len(results)}. {title} | {author} | {date}")

        print(f"\nFound {len(results)} articles:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.title} by {r.author} ({r.date})")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return MediumSearchResult(query=query, articles=results)


def test_search_medium() -> None:
    request = MediumSearchRequest(query="machine learning", max_results=5)
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
            result = search_medium(page, request)
            assert result.query == request.query
            assert len(result.articles) <= request.max_results
            print(f"\nTotal articles found: {len(result.articles)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_medium)
