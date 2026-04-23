"""
Playwright script (Python) — CNN.com Tech Headlines
Navigate to the Tech section and extract top headlines with links.

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
class CnnTechHeadlinesRequest:
    max_results: int


@dataclass(frozen=True)
class CnnHeadline:
    title: str
    link: str


@dataclass(frozen=True)
class CnnTechHeadlinesResult:
    headlines: list[CnnHeadline]


# Navigates to CNN's Tech section and extracts up to max_results
# headlines with their title and link.
def get_cnn_tech_headlines(
    page: Page,
    request: CnnTechHeadlinesRequest,
) -> CnnTechHeadlinesResult:
    max_results = request.max_results

    print(f"  Max results: {max_results}\n")

    results: list[CnnHeadline] = []

    try:
        # ── Navigate ──────────────────────────────────────────────────────
        url = "https://www.cnn.com/business/tech"
        print(f"Loading {url}...")
        checkpoint(f"Navigate to {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        # ── Dismiss popups / cookie banners ───────────────────────────────
        for selector in [
            "button#onetrust-accept-btn-handler",
            "button:has-text('Accept')",
            "button:has-text('I Accept')",
            "button:has-text('No Thanks')",
        ]:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {selector}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        print(f"  URL: {page.url}")

        # ── Extract headlines ─────────────────────────────────────────────
        print(f"Extracting up to {max_results} Tech headlines...")

        links = page.locator("a[data-link-type='article']")
        count = links.count()
        print(f"  Found {count} article links total")

        seen_titles = set()
        for i in range(count):
            if len(results) >= max_results:
                break
            link = links.nth(i)
            try:
                title = link.inner_text(timeout=2000).strip()
                href = link.evaluate("el => el.getAttribute('href')") or ""

                if not title or len(title) < 10:
                    continue
                if title in seen_titles:
                    continue
                if "/tech/" not in href:
                    continue

                if href.startswith("/"):
                    href = f"https://www.cnn.com{href}"
                if "?" in href:
                    href = href.split("?")[0]

                seen_titles.add(title)
                results.append(CnnHeadline(
                    title=title,
                    link=href,
                ))
            except Exception:
                pass

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nTop Tech headlines on CNN:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.title}")
            print(f"     Link: {r.link}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return CnnTechHeadlinesResult(
        headlines=results,
    )


def test_get_cnn_tech_headlines() -> None:
    request = CnnTechHeadlinesRequest(
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
            result = get_cnn_tech_headlines(page, request)
            assert len(result.headlines) <= request.max_results
            print(f"\nTotal headlines found: {len(result.headlines)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_get_cnn_tech_headlines)
