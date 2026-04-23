"""
Playwright script (Python) — NPR Podcast Listing
List NPR podcasts with name and description.

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
class NprPodcastsRequest:
    max_results: int


@dataclass(frozen=True)
class NprPodcast:
    name: str
    description: str


@dataclass(frozen=True)
class NprPodcastsResult:
    podcasts: list[NprPodcast]


# Lists NPR podcasts from the podcasts-and-shows page, extracting
# up to max_results podcasts with name and description.
def list_npr_podcasts(
    page: Page,
    request: NprPodcastsRequest,
) -> NprPodcastsResult:
    max_results = request.max_results

    print(f"  Max results: {max_results}\n")

    results: list[NprPodcast] = []

    try:
        checkpoint("Navigate to https://www.npr.org/podcasts-and-shows")
        page.goto("https://www.npr.org/podcasts-and-shows")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(4000)

        h3s = page.locator("h3")
        count = h3s.count()
        skip = {"New and Notable", "Daily News", "Culture and Entertainment", "Music",
                "Learn Something New", "Deep Dive", "From the NPR Network", "Cookie Settings"}

        for i in range(count):
            if len(results) >= max_results:
                break
            name = h3s.nth(i).inner_text(timeout=2000).strip()
            if not name or name in skip:
                continue
            desc = "N/A"
            try:
                parent_text = h3s.nth(i).evaluate("el => el.parentElement?.innerText || ''")
                lines = [l.strip() for l in parent_text.split("\n") if l.strip() and l.strip() != name]
                if lines:
                    desc = lines[0][:200]
            except Exception:
                pass
            results.append(NprPodcast(name=name, description=desc))
            print(f"  {len(results)}. {name} — {desc[:80]}")

        print(f"\nFound {len(results)} podcasts:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name}\n     {r.description[:100]}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return NprPodcastsResult(podcasts=results)


def test_list_npr_podcasts() -> None:
    request = NprPodcastsRequest(max_results=5)
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
            result = list_npr_podcasts(page, request)
            assert len(result.podcasts) <= request.max_results
            print(f"\nTotal podcasts found: {len(result.podcasts)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_list_npr_podcasts)
