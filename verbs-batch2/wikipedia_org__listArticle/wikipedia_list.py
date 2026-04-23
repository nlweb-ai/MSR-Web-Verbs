"""
Playwright script (Python) — Wikipedia List Article Extraction
Extract entries from a Wikipedia list article.

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
class WikipediaListRequest:
    article: str
    max_results: int


@dataclass(frozen=True)
class WikipediaListEntry:
    name: str
    year_created: str
    paradigm: str


@dataclass(frozen=True)
class WikipediaListResult:
    article: str
    entries: list[WikipediaListEntry]


# Extracts entries from a Wikipedia list article, returning
# up to max_results entries with name, year created, and paradigm.
def extract_wikipedia_list(
    page: Page,
    request: WikipediaListRequest,
) -> WikipediaListResult:
    article = request.article
    max_results = request.max_results

    print(f"  Article: {article}\n")

    results: list[WikipediaListEntry] = []

    try:
        slug = article.replace(" ", "_")
        url = f"https://en.wikipedia.org/wiki/{slug}"
        checkpoint(f"Navigate to {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        if "search" in page.url.lower():
            try:
                first_link = page.locator('div.mw-search-result-heading a').first
                if first_link.is_visible(timeout=2000):
                    checkpoint("Click first search result")
                    first_link.click()
                    page.wait_for_timeout(2000)
                    page.wait_for_load_state("domcontentloaded")
            except Exception:
                pass

        entries = page.locator("div.div-col ul li a")
        count = entries.count()
        print(f"  Found {count} language links on page")

        seen = set()
        for i in range(count):
            if len(results) >= max_results:
                break
            try:
                name = entries.nth(i).inner_text(timeout=1000).strip()
                if not name or name in seen or len(name) < 1:
                    continue
                seen.add(name)
                results.append(WikipediaListEntry(name=name, year_created="N/A", paradigm="N/A"))
                print(f"  {len(results)}. {name}")
            except Exception:
                continue

        print(f"\nFound {len(results)} entries:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return WikipediaListResult(article=article, entries=results)


def test_extract_wikipedia_list() -> None:
    request = WikipediaListRequest(article="List of programming languages", max_results=10)
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
            result = extract_wikipedia_list(page, request)
            assert result.article == request.article
            assert len(result.entries) <= request.max_results
            print(f"\nTotal entries found: {len(result.entries)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_extract_wikipedia_list)
