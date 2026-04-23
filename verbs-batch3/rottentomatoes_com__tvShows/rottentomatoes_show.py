import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


SEASONS_RE = re.compile(r'(\d+) Seasons?')
SCORE_RE = re.compile(r'^(\d+)%$')


@dataclass(frozen=True)
class RottenTomatoesTvShowRequest:
    slug: str
    show: str


@dataclass(frozen=True)
class RottenTomatoesTvShowResult:
    show: str
    tomatometer: str
    audience_score: str
    seasons: str
    synopsis: str


# Look up a TV show on Rotten Tomatoes by slug and extract
# Tomatometer score, audience score, number of seasons, and synopsis.
def rottentomatoes_tv_show_lookup(page: Page, request: RottenTomatoesTvShowRequest) -> RottenTomatoesTvShowResult:
    print(f"  Show: {request.show}\n")

    url = f"https://www.rottentomatoes.com/tv/{request.slug}"
    print(f"Loading {url}...")
    checkpoint("Navigate to page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    tomatometer = 'N/A'
    audience_score = 'N/A'
    seasons = 'N/A'
    synopsis = 'N/A'

    for i, line in enumerate(text_lines):
        # Tomatometer
        if 'Tomatometer' in line and i > 0:
            sm = SCORE_RE.match(text_lines[i - 1])
            if sm:
                tomatometer = sm.group(1) + '%'

        # Audience score (Popcornmeter)
        if 'Popcornmeter' in line and i > 0:
            sm = SCORE_RE.match(text_lines[i - 1])
            if sm:
                audience_score = sm.group(1) + '%'

        # Seasons from info line
        sm = SEASONS_RE.search(line)
        if sm:
            seasons = sm.group(1)

        # Synopsis
        if line == 'Synopsis' and i + 1 < len(text_lines):
            synopsis = text_lines[i + 1]

    result = RottenTomatoesTvShowResult(
        show=request.show,
        tomatometer=tomatometer,
        audience_score=audience_score,
        seasons=seasons,
        synopsis=synopsis,
    )

    print("=" * 60)
    print(f"{result.show} - Rotten Tomatoes")
    print("=" * 60)
    print(f"Tomatometer:    {result.tomatometer}")
    print(f"Audience Score: {result.audience_score}")
    print(f"Seasons:        {result.seasons}")
    print(f"\nSynopsis:\n{result.synopsis}")

    return result


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_user_data = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            chrome_user_data,
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        request = RottenTomatoesTvShowRequest(slug="severance", show="Severance")
        result = rottentomatoes_tv_show_lookup(page, request)
        print(f"\nResult: {result}")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)