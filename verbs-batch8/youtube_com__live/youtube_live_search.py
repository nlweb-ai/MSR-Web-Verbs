"""
YouTube – Browse current live streams

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class YoutubeLiveSearchRequest:
    search_query: str = "music"
    max_results: int = 5


@dataclass
class YoutubeLiveItem:
    video_title: str = ""
    channel_name: str = ""
    viewer_count: str = ""
    started_time: str = ""
    category: str = ""
    url: str = ""


@dataclass
class YoutubeLiveSearchResult:
    items: List[YoutubeLiveItem] = field(default_factory=list)


# Browse current live streams on YouTube.
def youtube_live_search(page: Page, request: YoutubeLiveSearchRequest) -> YoutubeLiveSearchResult:
    """Browse current live streams on YouTube."""
    print(f"  Search query: {request.search_query}")
    print(f"  Max results: {request.max_results}\n")

    url = f"https://www.youtube.com/results?search_query={request.search_query}&sp=EgJAAQ%253D%253D"
    print(f"Loading {url}...")
    checkpoint("Navigate to YouTube live search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = YoutubeLiveSearchResult()

    checkpoint("Extract live stream listings")
    js_code = """(max) => {
        const renderers = document.querySelectorAll('ytd-video-renderer, ytd-rich-item-renderer');
        const items = [];
        for (const r of renderers) {
            if (items.length >= max) break;
            const titleEl = r.querySelector('#video-title, a#video-title-link, h3 a');
            const channelEl = r.querySelector('#channel-name a, ytd-channel-name a, [class*="channel"] a');
            const viewerEl = r.querySelector('[class*="viewer"], [class*="watching"], .ytd-badge-supported-renderer, [class*="live-badge"]');
            const metaEl = r.querySelector('#metadata-line span, .ytd-video-meta-block span');
            const categoryEl = r.querySelector('[class*="category"], [class*="badge"]');

            const video_title = titleEl ? titleEl.textContent.trim() : '';
            const channel_name = channelEl ? channelEl.textContent.trim() : '';
            const viewer_count = viewerEl ? viewerEl.textContent.trim() : (metaEl ? metaEl.textContent.trim() : '');
            const started_time = '';
            const category = categoryEl ? categoryEl.textContent.trim() : '';
            const url = titleEl ? (titleEl.href || '') : '';

            if (video_title) {
                items.push({video_title, channel_name, viewer_count, started_time, category, url});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = YoutubeLiveItem()
        item.video_title = d.get("video_title", "")
        item.channel_name = d.get("channel_name", "")
        item.viewer_count = d.get("viewer_count", "")
        item.started_time = d.get("started_time", "")
        item.category = d.get("category", "")
        item.url = d.get("url", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Live Stream {i}:")
        print(f"    Title:    {item.video_title}")
        print(f"    Channel:  {item.channel_name}")
        print(f"    Viewers:  {item.viewer_count}")
        print(f"    Started:  {item.started_time}")
        print(f"    Category: {item.category}")
        print(f"    URL:      {item.url}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("youtube_live")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = YoutubeLiveSearchRequest()
            result = youtube_live_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} live streams")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
