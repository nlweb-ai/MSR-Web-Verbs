import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


SCORE_RE = re.compile(r'^\d+\.?\d*$')
REVIEWS_RE = re.compile(r'^Based on ([\d,]+) (Critic Reviews|User Ratings)$')


@dataclass(frozen=True)
class MetacriticGameRequest:
    game_slug: str
    game_title: str


@dataclass(frozen=True)
class MetacriticGameResult:
    game: str
    release_date: str | None
    metascore: str | None
    meta_label: str | None
    meta_reviews: str | None
    user_score: str | None
    user_label: str | None
    user_ratings: str | None
    platform: str | None
    critic_summary: str | None


# Search for a game on Metacritic by slug and extract the Metascore, user score,
# platform, release date, and critic review summary from the game's page.
def metacritic_game(page: Page, request: MetacriticGameRequest) -> MetacriticGameResult:
    print(f"  Game: {request.game_title}")

    url = f"https://www.metacritic.com/game/{request.game_slug}/"
    print(f"Loading {url}...")
    checkpoint("Navigate to page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    metascore = None
    meta_label = None
    meta_reviews = None
    user_score = None
    user_label = None
    user_ratings = None
    release_date = None
    platform = None
    critic_summary = None

    i = 0
    found_main_meta = False
    while i < len(text_lines):
        line = text_lines[i]

        if line.startswith('Released On'):
            release_date = re.sub(r'^Released\s+On:?\s*', '', line)

        if line == "METASCORE" and not found_main_meta:
            found_main_meta = True
            for j in range(i + 1, min(i + 5, len(text_lines))):
                jline = text_lines[j]
                m = REVIEWS_RE.match(jline)
                if m and 'Critic' in m.group(2):
                    meta_reviews = m.group(1)
                elif SCORE_RE.match(jline) and not metascore:
                    val = jline
                    if '.' not in val and int(val) <= 100:
                        metascore = val
                elif jline in ('Universal Acclaim', 'Generally Favorable', 'Mixed or Average Reviews', 'Generally Unfavorable'):
                    meta_label = jline

        if line == "USER SCORE" and not user_score:
            for j in range(i + 1, min(i + 5, len(text_lines))):
                jline = text_lines[j]
                m = REVIEWS_RE.match(jline)
                if m and 'User' in m.group(2):
                    user_ratings = m.group(1)
                elif SCORE_RE.match(jline) and '.' in jline:
                    user_score = jline
                elif jline in ('Generally Favorable', 'Mixed or Average Reviews', 'Generally Unfavorable', 'Universal Acclaim'):
                    user_label = jline

        if line in ('PLAYSTATION 5', 'PLAYSTATION 4', 'PC', 'XBOX SERIES X', 'XBOX ONE', 'NINTENDO SWITCH') and not platform:
            platform = line

        if not critic_summary and len(line) > 100 and i > 10:
            critic_summary = line

        i += 1

    print("=" * 60)
    print(f"Metacritic: {request.game_title}")
    print("=" * 60)
    print(f"\nRelease Date: {release_date or 'N/A'}")
    print(f"\nMetascore:    {metascore or 'N/A'} ({meta_label or 'N/A'})")
    print(f"  Based on:   {meta_reviews or 'N/A'} Critic Reviews")
    print(f"\nUser Score:   {user_score or 'N/A'} ({user_label or 'N/A'})")
    print(f"  Based on:   {user_ratings or 'N/A'} User Ratings")
    print(f"\nPlatform:     {platform or 'N/A'}")
    print(f"\nCritic Summary:")
    if critic_summary:
        print(f"  {critic_summary[:200]}...")
    else:
        print('  N/A')

    return MetacriticGameResult(
        game=request.game_title,
        release_date=release_date,
        metascore=metascore,
        meta_label=meta_label,
        meta_reviews=meta_reviews,
        user_score=user_score,
        user_label=user_label,
        user_ratings=user_ratings,
        platform=platform,
        critic_summary=critic_summary,
    )


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
        request = MetacriticGameRequest(game_slug="elden-ring", game_title="Elden Ring")
        result = metacritic_game(page, request)
        print(f"\nResult: {result}")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)