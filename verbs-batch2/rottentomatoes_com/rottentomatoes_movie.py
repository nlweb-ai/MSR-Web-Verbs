"""
Playwright script (Python) — Rotten Tomatoes Movie Info
Look up a movie and extract Tomatometer, audience score, and synopsis.

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
class RottenTomatoesMovieRequest:
    movie_name: str


@dataclass(frozen=True)
class RottenTomatoesMovieResult:
    movie_name: str
    tomatometer: str
    audience_score: str
    synopsis: str


# Looks up a movie on Rotten Tomatoes and extracts the Tomatometer score,
# audience score, and synopsis.
def lookup_rottentomatoes_movie(
    page: Page,
    request: RottenTomatoesMovieRequest,
) -> RottenTomatoesMovieResult:
    movie_name = request.movie_name

    print(f"  Movie: {movie_name}\n")

    tomatometer = "N/A"
    audience_score = "N/A"
    synopsis = "N/A"

    try:
        slug = re.sub(r'[^a-z0-9]+', '_', movie_name.lower()).strip('_')
        url = f"https://www.rottentomatoes.com/m/{slug}"
        checkpoint(f"Navigate to {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        body_text = page.locator("body").inner_text(timeout=5000)

        if "404" in page.title() or "not found" in body_text.lower()[:200]:
            search_url = f"https://www.rottentomatoes.com/search?search={movie_name.replace(' ', '+')}"
            checkpoint(f"Navigate to search: {search_url}")
            page.goto(search_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(4000)
            first = page.locator('search-page-media-row').first
            checkpoint("Click first search result")
            first.locator('a').first.click()
            page.wait_for_timeout(3000)
            body_text = page.locator("body").inner_text(timeout=5000)

        tm = re.search(r"(\d+)%\s*Tomatometer", body_text)
        tomatometer = f"{tm.group(1)}%" if tm else "N/A"
        am = re.search(r"(\d+)%\s*Popcornmeter", body_text)
        if not am:
            am = re.search(r"(\d+)%\s*Audience", body_text)
        audience_score = f"{am.group(1)}%" if am else "N/A"

        try:
            lines = body_text.split("\n")
            for l in lines:
                l = l.strip()
                if len(l) > 100 and "%" not in l[:10] and "Cookie" not in l:
                    synopsis = l[:500]
                    break
        except Exception:
            pass

        print(f"Movie: {movie_name}")
        print(f"  Tomatometer:    {tomatometer}")
        print(f"  Audience Score: {audience_score}")
        print(f"  Synopsis:       {synopsis[:200]}...")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return RottenTomatoesMovieResult(movie_name=movie_name, tomatometer=tomatometer, audience_score=audience_score, synopsis=synopsis)


def test_lookup_rottentomatoes_movie() -> None:
    request = RottenTomatoesMovieRequest(movie_name="Inception")
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
            result = lookup_rottentomatoes_movie(page, request)
            assert result.movie_name == request.movie_name
            print(f"\nMovie lookup complete for: {result.movie_name}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_lookup_rottentomatoes_movie)
