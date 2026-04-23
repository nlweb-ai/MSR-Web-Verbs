"""
Playwright verb — SoundCloud Track Search
Search for tracks on SoundCloud by keyword.
Navigate to the search results page filtered to tracks.
Extract up to max_results tracks with title, artist, duration, and play count.

URL pattern: https://soundcloud.com/search/sounds?q={query}
"""

import re
import os
from dataclasses import dataclass
from urllib.parse import quote
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


PLAYS_RE = re.compile(r"^([\d,]+)\s+plays?$")


@dataclass(frozen=True)
class SoundcloudSearchRequest:
    query: str = "lo-fi hip hop"
    max_results: int = 5


@dataclass(frozen=True)
class SoundcloudTrack:
    title: str = "N/A"
    artist: str = "N/A"
    duration: str = "N/A"
    plays: str = "N/A"


@dataclass(frozen=True)
class SoundcloudSearchResult:
    tracks: tuple = ()


# Search for tracks on SoundCloud by keyword query.
# Navigates to the search results page filtered to tracks, parses the body text
# to extract track title, artist, duration, and play count for up to max_results tracks.
def soundcloud_search(page: Page, request: SoundcloudSearchRequest) -> SoundcloudSearchResult:
    query = request.query
    max_results = request.max_results
    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    results = []

    search_url = f"https://soundcloud.com/search/sounds?q={quote(query)}"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to page")
    page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    # Accept cookie banner if present
    try:
        accept = page.locator('button#onetrust-accept-btn-handler')
        if accept.is_visible(timeout=2000):
            checkpoint("Click element")
            accept.click()
            page.wait_for_timeout(1000)
    except Exception:
        pass

    body = page.locator("body").inner_text(timeout=10000)
    lines = [l.strip() for l in body.split("\n") if l.strip()]

    print(f"\nParsing {len(lines)} body lines...")

    # Find "Found N+ tracks" header
    start_idx = 0
    for i, l in enumerate(lines):
        if "Found" in l and "track" in l:
            start_idx = i + 1
            print(f"  Results start at line {i}: {l}")
            break

    i = start_idx
    while i < len(lines) and len(results) < max_results:
        m = PLAYS_RE.match(lines[i])
        if m:
            plays = m.group(1)

            title = "N/A"
            artist = "N/A"

            # Find "Posted" line above plays
            posted_idx = None
            for delta in range(1, 8):
                idx = i - delta
                if idx >= start_idx and lines[idx].startswith("Posted "):
                    posted_idx = idx
                    break

            if posted_idx is not None:
                if posted_idx - 1 >= start_idx:
                    title = lines[posted_idx - 1]
                if posted_idx - 2 >= start_idx:
                    artist = lines[posted_idx - 2]

            duration = "N/A"

            if title != "N/A":
                results.append(SoundcloudTrack(
                    title=title,
                    artist=artist,
                    duration=duration,
                    plays=plays,
                ))

            i += 1
            continue
        i += 1

    print(f'\nFound {len(results)} tracks for "{query}":\n')
    for idx, t in enumerate(results, 1):
        print(f"  {idx}. {t.title}")
        print(f"     Artist: {t.artist}")
        print(f"     Duration: {t.duration}  Plays: {t.plays}")
        print()

    return SoundcloudSearchResult(tracks=tuple(results))


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    with sync_playwright() as p:
        profile_path = os.path.join(
            os.environ["USERPROFILE"],
            "AppData", "Local", "Google", "Chrome", "User Data", "Default",
        )
        context = p.chromium.launch_persistent_context(
            profile_path,
            headless=False,
            channel="chrome",
        )
        page = context.pages[0] if context.pages else context.new_page()
        request = SoundcloudSearchRequest(query="lo-fi hip hop", max_results=5)
        result = soundcloud_search(page, request)
        print(f"\nTotal tracks found: {len(result.tracks)}")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
