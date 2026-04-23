"""
Auto-generated Playwright script (Python)
Vimeo – Video Search

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class SearchRequest:
    search_query: str = "short film documentary"
    max_results: int = 5


@dataclass
class VideoResult:
    title: str = ""
    creator: str = ""
    duration: str = ""
    views: str = ""
    likes: str = ""


@dataclass
class SearchResult:
    videos: List[VideoResult] = field(default_factory=list)


def vimeo_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search Vimeo for videos."""
    print(f"  Query: {request.search_query}\n")

    query_encoded = request.search_query.replace(" ", "+")
    url = f"https://vimeo.com/search?q={query_encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = SearchResult()

    checkpoint("Extract video results")
    # Pattern per video: likes_count, ?, duration, title, creator, views_info, date
    js_code = r"""(max) => {
        const lines = document.body.innerText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find start - after "Filters" line near top
        let startIdx = 0;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === 'Filters' && i < 20) { startIdx = i + 1; break; }
        }
        const videos = [];
        let i = startIdx;
        while (i < lines.length && videos.length < max) {
            // First number is likes count
            if (!/^\d[\d,.]*$/.test(lines[i])) { i++; continue; }
            const likes = lines[i]; i++;
            // Second number (could be another count)
            if (i < lines.length && /^\d[\d,.]*$/.test(lines[i])) i++;
            // Duration (MM:SS format)
            let duration = '';
            if (i < lines.length && /^\d+:\d+$/.test(lines[i])) {
                duration = lines[i]; i++;
            }
            // Title
            let title = '';
            if (i < lines.length) { title = lines[i]; i++; }
            // Creator
            let creator = '';
            if (i < lines.length) { creator = lines[i]; i++; }
            // Views + date line (e.g. "92.6K views • July 27, 2016")
            let views = '';
            if (i < lines.length) {
                const viewLine = lines[i];
                const viewMatch = viewLine.match(/([\d,.]+K?)\s*views/);
                if (viewMatch) views = viewMatch[1] + ' views';
                i++;
            }
            if (title && duration) {
                videos.push({title, creator, duration, views, likes});
            }
        }
        return videos;
    }"""
    videos_data = page.evaluate(js_code, request.max_results)

    for vd in videos_data:
        v = VideoResult()
        v.title = vd.get("title", "")
        v.creator = vd.get("creator", "")
        v.duration = vd.get("duration", "")
        v.views = vd.get("views", "")
        v.likes = vd.get("likes", "")
        result.videos.append(v)

    for i, v in enumerate(result.videos, 1):
        print(f"\n  Video {i}:")
        print(f"    Title:    {v.title}")
        print(f"    Creator:  {v.creator}")
        print(f"    Duration: {v.duration}")
        print(f"    Views:    {v.views}")
        print(f"    Likes:    {v.likes}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("vimeo")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = vimeo_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.videos)} videos")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
