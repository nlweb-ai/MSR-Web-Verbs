"""
Auto-generated Playwright script (Python)
YouTube Video Search: "anchorage museums"

Generated on: 2026-02-26T18:57:25.156Z
Recorded 11 browser interactions
Note: This script was generated using AI-driven discovery patterns
"""

import re
import os
from playwright.sync_api import Page, sync_playwright, expect

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws, find_chrome_executable
from playwright_debugger import checkpoint
import shutil

from dataclasses import dataclass
import subprocess
import tempfile
import json
import time
from urllib.request import urlopen


@dataclass(frozen=True)
class YouTubeSearchRequest:
    search_query: str = "anchorage museums"
    max_results: int = 5


@dataclass(frozen=True)
class YouTubeVideo:
    url: str
    title: str
    duration: str


@dataclass(frozen=True)
class YouTubeSearchResult:
    search_query: str
    videos: list[YouTubeVideo]
def search_youtube_videos(page: Page, request: YouTubeSearchRequest) -> YouTubeSearchResult:
    """
    Search YouTube for the given query and return up to request.max_results video results,
    each with url, title, and duration.
    """
    results = []

    try:
        # Navigate to YouTube
        checkpoint("Navigate to YouTube homepage")
        page.goto("https://www.youtube.com")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        # Find and fill the search box
        search_input = page.get_by_role("combobox", name=re.compile(r"Search", re.IGNORECASE)).first
        checkpoint("Click search input")
        search_input.evaluate("el => el.click()")
        checkpoint("Fill search query")
        search_input.fill(request.search_query)
        page.wait_for_timeout(500)

        # Submit the search
        checkpoint("Press Enter to submit search")
        search_input.press("Enter")

        # Wait for search results to load
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)

        # Extract video results
        # YouTube video links have /watch?v= in the href
        # Duration is shown as overlay text on the thumbnail
        video_renderers = page.locator("ytd-video-renderer")
        count = video_renderers.count()
        if count == 0:
            # Fallback: try the general video list item
            video_renderers = page.locator("#contents ytd-video-renderer, #contents ytd-rich-item-renderer")
            count = video_renderers.count()

        for i in range(min(count, request.max_results)):
            renderer = video_renderers.nth(i)
            try:
                # Get the video URL and title from the title link
                title_link = renderer.locator("a#video-title").first
                href = title_link.get_attribute("href", timeout=2000) or ""
                if not href.startswith("http"):
                    href = "https://www.youtube.com" + href
                title = title_link.inner_text(timeout=2000).strip()

                # Get the duration from the time-status overlay
                duration = "N/A"
                try:
                    time_el = renderer.locator("span#text.ytd-thumbnail-overlay-time-status-renderer, badge-shape .badge-shape-wiz__text, span.ytd-thumbnail-overlay-time-status-renderer").first
                    duration = time_el.inner_text(timeout=2000).strip()
                except Exception:
                    # Try alternative: the time display in the thumbnail
                    try:
                        time_el = renderer.locator("[overlay-style='DEFAULT'] span").first
                        duration = time_el.inner_text(timeout=2000).strip()
                    except Exception:
                        pass

                results.append({"url": href, "title": title, "duration": duration})
            except Exception:
                continue

        if not results:
            # Fallback: extract video links from page
            print("Primary extraction failed, trying link-based fallback...")
            all_links = page.get_by_role("link").all()
            seen = set()
            for link in all_links:
                try:
                    href = link.get_attribute("href", timeout=500) or ""
                    if "/watch?v=" in href and href not in seen:
                        seen.add(href)
                        if not href.startswith("http"):
                            href = "https://www.youtube.com" + href
                        label = link.inner_text(timeout=500).strip() or "N/A"
                        results.append({"url": href, "title": label, "duration": "N/A"})
                        if len(results) >= request.max_results:
                            break
                except Exception:
                    continue

        if not results:
            print("Warning: Could not find any video results.")

        # Print results
        print(f"\nFound {len(results)} video results for '{request.search_query}':\n")
        for i, item in enumerate(results, 1):
            print(f"  {i}. {item['title']}")
            print(f"     URL: {item['url']}")
            print(f"     Duration: {item['duration']}")

    except Exception as e:
        print(f"Error searching YouTube: {e}")
    return YouTubeSearchResult(
        search_query=request.search_query,
        videos=[YouTubeVideo(url=r['url'], title=r['title'], duration=r['duration']) for r in results],
    )


def test_youtube_videos():
    from playwright.sync_api import sync_playwright
    request = YouTubeSearchRequest(search_query="anchorage museums", max_results=5)
    port = get_free_port()
    profile_dir = tempfile.mkdtemp(prefix="chrome_cdp_")
    chrome = os.environ.get("CHROME_PATH") or find_chrome_executable()
    chrome_proc = subprocess.Popen(
        [
            chrome,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={profile_dir}",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1280,987",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    ws_url = None
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            resp = urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2)
            ws_url = json.loads(resp.read()).get("webSocketDebuggerUrl", "")
            if ws_url:
                break
        except Exception:
            pass
        time.sleep(0.4)
    if not ws_url:
        raise TimeoutError("Chrome CDP not ready")
    with sync_playwright() as pl:
        browser = pl.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_youtube_videos(page, request)
        finally:
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)
    print(f"\nSearch: {result.search_query}")
    print(f"Total videos: {len(result.videos)}")
    for i, v in enumerate(result.videos, 1):
        print(f"  {i}. {v.title}  ({v.duration})")
        print(f"     {v.url}")


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_youtube_videos)
