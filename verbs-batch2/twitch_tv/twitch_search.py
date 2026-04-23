"""
Playwright script (Python) — Twitch Stream Search
Search for live streams and extract streamer, viewers, and title.

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
class TwitchSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class TwitchStream:
    streamer: str
    viewers: str
    title: str


@dataclass(frozen=True)
class TwitchSearchResult:
    query: str
    streams: list[TwitchStream]


# Searches Twitch for live streams matching a query, then extracts
# up to max_results streams with streamer name, viewer count, and title.
def search_twitch(
    page: Page,
    request: TwitchSearchRequest,
) -> TwitchSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}\n")

    results: list[TwitchStream] = []

    try:
        url = f"https://www.twitch.tv/search?term={query.replace(' ', '+')}"
        checkpoint(f"Navigate to {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)

        body = page.locator("body").inner_text(timeout=5000)
        lines = [l.strip() for l in body.split("\n") if l.strip()]
        start = 0
        for i, line in enumerate(lines):
            if line == "Channels":
                start = i + 1
                break

        i = start
        while i < len(lines) and len(results) < max_results:
            if i + 3 <= len(lines) and lines[i + 2].upper().endswith("VIEWERS") and lines[i + 3] == "LIVE":
                streamer = lines[i]
                game = lines[i + 1]
                viewers = lines[i + 2]
                results.append(TwitchStream(streamer=streamer, viewers=viewers, title=game))
                print(f"  {len(results)}. {streamer} | {viewers} | {game}")
                i += 4
            elif i + 4 <= len(lines) and "LIVE" in lines[i + 3]:
                streamer = lines[i]
                game = lines[i + 1] if not lines[i + 1].endswith("Viewers") else "N/A"
                viewers = "N/A"
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].upper().endswith("VIEWERS"):
                        viewers = lines[j]
                        break
                if viewers != "N/A":
                    results.append(TwitchStream(streamer=streamer, viewers=viewers, title=game))
                    print(f"  {len(results)}. {streamer} | {viewers} | {game}")
                i += 4
            else:
                i += 1

        print(f"\nFound {len(results)} streams:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.streamer} ({r.viewers}) — {r.title}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return TwitchSearchResult(query=query, streams=results)


def test_search_twitch() -> None:
    request = TwitchSearchRequest(query="Minecraft", max_results=5)
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
            result = search_twitch(page, request)
            assert result.query == request.query
            assert len(result.streams) <= request.max_results
            print(f"\nTotal streams found: {len(result.streams)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_twitch)
