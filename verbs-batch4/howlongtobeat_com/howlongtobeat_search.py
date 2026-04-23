import re
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class HowLongToBeatRequest:
    query: str = "Elden Ring"

@dataclass(frozen=True)
class HowLongToBeatResult:
    game_title: str = ""
    main_story_time: str = ""
    main_extras_time: str = ""
    completionist_time: str = ""

# Search for a game on HowLongToBeat and extract completion time estimates.
def howlongtobeat_search(page: Page, request: HowLongToBeatRequest) -> HowLongToBeatResult:
    query = request.query
    print(f"  Search query: {query}\n")

    url = f"https://howlongtobeat.com/?q={quote_plus(query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to HowLongToBeat")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    game_title = ""
    main_story_time = ""
    main_extras_time = ""
    completionist_time = ""

    # Look for search result links and click the first one
    result_links = page.locator(
        'a[href*="game/"], '
        'a[href*="game?id="], '
        '[class*="GameCard"], '
        '[class*="search_list"] a, '
        'li a[href*="game"]'
    )
    count = result_links.count()
    print(f"  Found {count} result links")

    if count > 0:
        first_result = result_links.first
        try:
            game_title = first_result.inner_text(timeout=3000).strip().split("\n")[0].strip()
            print(f"  Clicking first result: {game_title}")
            first_result.click(timeout=5000)
            page.wait_for_timeout(5000)
            print(f"  Game page loaded: {page.url}")
        except Exception as e:
            print(f"  Error clicking result: {e}")

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""

    # Try extracting times from game detail page using known label patterns
    # HowLongToBeat typically shows: Main Story, Main + Extras, Completionist
    time_pattern = r'(\d+[\d½¼¾]*\s*(?:Hours?|Mins?|h|m|½)?(?:\s*\d+\s*(?:Mins?|m))?)'

    # Try structured extraction via game detail sections
    detail_sections = page.locator(
        '[class*="GameStats"], '
        '[class*="game_times"], '
        '[class*="GameTimeStat"], '
        '[class*="time_"], '
        '[class*="GameDetail"]'
    )
    detail_count = detail_sections.count()
    print(f"  Found {detail_count} detail sections")

    if detail_count > 0:
        for i in range(detail_count):
            try:
                section_text = detail_sections.nth(i).inner_text(timeout=3000).strip()
                lines = [l.strip() for l in section_text.split("\n") if l.strip()]
                for j, line in enumerate(lines):
                    lower = line.lower()
                    # Look for time value in the next line or same line
                    time_val = ""
                    if j + 1 < len(lines):
                        tm = re.search(time_pattern, lines[j + 1], re.IGNORECASE)
                        if tm:
                            time_val = tm.group(1).strip()
                    if not time_val:
                        tm = re.search(time_pattern, line, re.IGNORECASE)
                        if tm:
                            time_val = tm.group(1).strip()

                    if "main story" in lower or "main" == lower.strip():
                        if time_val and not main_story_time:
                            main_story_time = time_val
                    elif "main + extra" in lower or "main+extra" in lower or "extras" in lower:
                        if time_val and not main_extras_time:
                            main_extras_time = time_val
                    elif "completionist" in lower or "complete" in lower:
                        if time_val and not completionist_time:
                            completionist_time = time_val
            except Exception:
                continue

    # Fallback: text-based extraction from full page
    if not main_story_time or not main_extras_time or not completionist_time:
        print("  Trying text-based extraction fallback...")
        text_lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        for j, line in enumerate(text_lines):
            lower = line.lower()
            # Search forward from label for a time value
            time_val = ""
            for k in range(j, min(len(text_lines), j + 4)):
                tm = re.search(time_pattern, text_lines[k], re.IGNORECASE)
                if tm:
                    time_val = tm.group(1).strip()
                    break

            if ("main story" in lower or lower == "main") and not main_story_time and time_val:
                main_story_time = time_val
            elif ("main + extra" in lower or "main+extra" in lower or "extras" in lower) and not main_extras_time and time_val:
                main_extras_time = time_val
            elif ("completionist" in lower or "completionists" in lower) and not completionist_time and time_val:
                completionist_time = time_val

        # Try to get game title from page if not already set
        if not game_title:
            title_el = page.locator(
                '[class*="GameHeader"] h1, '
                '[class*="profile_header"] h1, '
                'h1, h2'
            )
            if title_el.count() > 0:
                try:
                    game_title = title_el.first.inner_text(timeout=3000).strip()
                except Exception:
                    pass
            if not game_title:
                game_title = query

    print("=" * 60)
    print(f"HowLongToBeat - Results for \"{query}\"")
    print("=" * 60)
    print(f"  Game Title:        {game_title}")
    print(f"  Main Story:        {main_story_time}")
    print(f"  Main + Extras:     {main_extras_time}")
    print(f"  Completionist:     {completionist_time}")

    return HowLongToBeatResult(
        game_title=game_title,
        main_story_time=main_story_time,
        main_extras_time=main_extras_time,
        completionist_time=completionist_time,
    )

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = howlongtobeat_search(page, HowLongToBeatRequest())
        print(f"\nGame: {result.game_title}")
        print(f"Main Story: {result.main_story_time}")
        print(f"Main + Extras: {result.main_extras_time}")
        print(f"Completionist: {result.completionist_time}")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
