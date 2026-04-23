"""
Playwright script (Python) — edX.org Course Search
Search for courses matching a query, extract title, institution, and duration.

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
class EdxSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class EdxCourse:
    title: str
    institution: str
    duration: str


@dataclass(frozen=True)
class EdxSearchResult:
    query: str
    courses: list[EdxCourse]


# Searches edX.org for courses matching a query and extracts up to
# max_results courses with title, institution, and duration.
def search_edx_courses(
    page: Page,
    request: EdxSearchRequest,
) -> EdxSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    results: list[EdxCourse] = []

    try:
        # ── Navigate ──────────────────────────────────────────────────────
        print("Loading edX.org...")
        checkpoint("Navigate to https://www.edx.org")
        page.goto("https://www.edx.org")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # ── Dismiss popups / cookie banners ───────────────────────────────
        for selector in [
            "button#onetrust-accept-btn-handler",
            "button:has-text('Accept')",
            "button:has-text('Got it')",
            "button:has-text('Close')",
        ]:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {selector}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        # ── STEP 1: Search ────────────────────────────────────────────────
        print(f'STEP 1: Search for "{query}"...')
        search_input = page.locator(
            'input[data-testid="search-input"], '
            'input[name="q"], '
            'input[aria-label*="search" i], '
            'input[placeholder*="search" i], '
            'input[type="search"]'
        ).first
        checkpoint("Click search input")
        search_input.evaluate("el => el.click()")
        page.wait_for_timeout(500)
        page.keyboard.press("Control+a")
        checkpoint(f"Type query: {query}")
        search_input.type(query, delay=50)
        page.wait_for_timeout(1000)
        checkpoint("Press Enter to search")
        page.keyboard.press("Enter")
        print(f'  Typed "{query}" and pressed Enter')
        page.wait_for_timeout(2000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # ── STEP 2: Extract courses ───────────────────────────────────────
        print(f"STEP 2: Extract up to {max_results} courses...")

        course_cards = page.locator(
            'div[class*="card"]'
        )
        count = course_cards.count()
        print(f"  Found {count} course cards")

        for i in range(min(count, max_results)):
            card = course_cards.nth(i)
            try:
                title = "N/A"
                institution = "N/A"
                duration = "N/A"

                card_text = card.inner_text(timeout=3000).strip()
                lines = [l.strip() for l in card_text.split("\n") if l.strip()]
                if len(lines) >= 2:
                    title = lines[1] if len(lines) > 1 else lines[0]
                if len(lines) >= 3:
                    institution = lines[2]
                for line in lines:
                    if any(w in line.lower() for w in ["week", "month", "complete", "hour"]):
                        duration = line
                        break

                if title != "N/A":
                    results.append(EdxCourse(
                        title=title,
                        institution=institution,
                        duration=duration,
                    ))
                    print(f"  {len(results)}. {title} | {institution} | {duration}")

            except Exception as e:
                print(f"  Error on card {i}: {e}")
                continue

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nFound {len(results)} courses for '{query}':")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.title}")
            print(f"     Institution: {r.institution}  Duration: {r.duration}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return EdxSearchResult(
        query=query,
        courses=results,
    )


def test_search_edx_courses() -> None:
    request = EdxSearchRequest(
        query="data science",
        max_results=5,
    )

    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=False,
            viewport=None,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_edx_courses(page, request)
            assert result.query == request.query
            assert len(result.courses) <= request.max_results
            print(f"\nTotal courses found: {len(result.courses)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_edx_courses)
