"""
YouTube – Trending Videos verb
Navigate to YouTube Trending page and extract trending video listings.
"""

import re
import os
from dataclasses import dataclass
from playwright.sync_api import Page, sync_playwright

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

# ── Types ─────────────────────────────────────────────────────────────────────

@dataclass
class YouTubeTrendingRequest:
    max_results: int    # number of trending videos to extract

@dataclass
class YouTubeTrendingVideo:
    title: str          # video title
    channel_name: str   # channel name
    view_count: str     # e.g. "1.2M views"
    upload_time: str    # e.g. "2 hours ago"

@dataclass
class YouTubeTrendingResult:
    videos: list  # list of YouTubeTrendingVideo

# ── Verb ──────────────────────────────────────────────────────────────────────

def youtube_trending(page: Page, request: YouTubeTrendingRequest) -> YouTubeTrendingResult:
    """
    Navigate to YouTube Trending and extract video listings.

    Args:
        page: Playwright page.
        request: YouTubeTrendingRequest with max_results.

    Returns:
        YouTubeTrendingResult containing a list of YouTubeTrendingVideo.
    """
    trending_url = "https://www.youtube.com/feed/trending"
    print(f"Loading {trending_url}...")
    page.goto(trending_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)
    current_url = page.url
    print(f"  Loaded: {current_url}")

    if "trending" not in current_url:
        print("  Trending page not accessible, using search fallback...")
        search_url = "https://www.youtube.com/results?search_query=trending+today&sp=CAI%253D"
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)
        print(f"  Loaded search: {page.url}")

    checkpoint("Loaded YouTube trending page")

    # Dismiss cookie / consent dialogs
    for selector in [
        'button[aria-label="Accept all"]',
        'button[aria-label="Accept the use of cookies and other data for the purposes described"]',
        'button:has-text("Accept all")',
        'button:has-text("Reject all")',
        'tp-yt-paper-dialog button#button',
    ]:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=1500):
                btn.click()
                page.wait_for_timeout(500)
                break
        except Exception:
            pass

    page.wait_for_timeout(2000)

    # Extract trending videos
    print(f"Extracting up to {request.max_results} trending videos...")

    video_renderers = page.locator("ytd-video-renderer")
    count = video_renderers.count()
    print(f"  Found {count} video renderers")

    results = []
    seen_titles = set()
    for i in range(count):
        if len(results) >= request.max_results:
            break
        renderer = video_renderers.nth(i)
        try:
            # Title
            title = "N/A"
            try:
                title_el = renderer.locator("#video-title").first
                title = title_el.inner_text(timeout=2000).strip()
            except Exception:
                pass

            if title == "N/A" or title.lower() in seen_titles:
                continue
            seen_titles.add(title.lower())

            # Channel name
            channel_name = "N/A"
            try:
                channel_el = renderer.locator(
                    "ytd-channel-name a, "
                    "#channel-name a, "
                    "#channel-name #text"
                ).first
                channel_name = channel_el.inner_text(timeout=2000).strip()
            except Exception:
                pass

            # Metadata line: views and upload time
            view_count = "N/A"
            upload_time = "N/A"
            try:
                meta_el = renderer.locator("#metadata-line span.inline-metadata-item, #metadata-line span")
                meta_count = meta_el.count()
                for mi in range(meta_count):
                    text = meta_el.nth(mi).inner_text(timeout=1000).strip()
                    if "view" in text.lower():
                        view_count = text
                    elif "ago" in text.lower():
                        upload_time = text
            except Exception:
                pass
            # Fallback: try aria-label on the video link
            if view_count == "N/A":
                try:
                    aria = renderer.locator("#video-title").first.get_attribute("aria-label", timeout=1000) or ""
                    vm = re.search(r"([\d,]+)\s*views?", aria, re.IGNORECASE)
                    if vm:
                        view_count = vm.group(0)
                    tm = re.search(r"(\d+\s+(?:seconds?|minutes?|hours?|days?|weeks?|months?|years?)\s+ago)", aria, re.IGNORECASE)
                    if tm:
                        upload_time = tm.group(1)
                except Exception:
                    pass

            results.append(YouTubeTrendingVideo(
                title=title,
                channel_name=channel_name,
                view_count=view_count,
                upload_time=upload_time,
            ))
        except Exception:
            continue

    # Fallback: regex on page text
    if not results:
        print("  Renderer extraction failed, trying text fallback...")
        body_text = page.evaluate("document.body.innerText") or ""
        lines = body_text.split("\n")
        for i, line in enumerate(lines):
            if len(results) >= request.max_results:
                break
            view_match = re.search(r"([\d,.]+[KMB]?)\s*views?", line, re.IGNORECASE)
            if view_match and len(line.strip()) < 200:
                title = "N/A"
                channel = "N/A"
                for j in range(max(0, i - 5), i):
                    cand = lines[j].strip()
                    if cand and len(cand) > 5 and "view" not in cand.lower():
                        if title == "N/A":
                            title = cand
                        else:
                            channel = cand
                upload_time = "N/A"
                time_match = re.search(r"(\d+\s+(?:second|minute|hour|day|week|month|year)s?\s+ago)", line, re.IGNORECASE)
                if time_match:
                    upload_time = time_match.group(1)

                if title != "N/A":
                    results.append(YouTubeTrendingVideo(
                        title=title,
                        channel_name=channel,
                        view_count=view_match.group(0),
                        upload_time=upload_time,
                    ))

    checkpoint("Extracted trending videos")
    print(f"\nFound {len(results)} trending videos:")
    for i, vid in enumerate(results, 1):
        print(f"  {i}. {vid.title}")
        print(f"     Channel: {vid.channel_name}  Views: {vid.view_count}  Uploaded: {vid.upload_time}")

    return YouTubeTrendingResult(videos=results)

# ── Test ──────────────────────────────────────────────────────────────────────

def test_func():

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()

        request = YouTubeTrendingRequest(max_results=10)
        result = youtube_trending(page, request)
        print(f"\nTotal trending videos found: {len(result.videos)}")

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
