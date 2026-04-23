"""
Auto-generated Playwright script (Python)
YouTube – Playlist Video Extraction

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
class PlaylistRequest:
    search_query: str = "Lo-Fi Hip Hop Radio"
    max_results: int = 10


@dataclass
class VideoResult:
    index: str = ""
    title: str = ""
    channel: str = ""
    duration: str = ""
    views_info: str = ""


@dataclass
class PlaylistResult:
    playlist_title: str = ""
    videos: List[VideoResult] = field(default_factory=list)


def youtube_playlist(page: Page, request: PlaylistRequest) -> PlaylistResult:
    """Search YouTube for a playlist and extract video info."""
    print(f"  Query: {request.search_query}\n")

    # Search YouTube filtered by playlists
    query_encoded = request.search_query.replace(" ", "+")
    search_url = f"https://www.youtube.com/results?search_query={query_encoded}&sp=EgIQAw%3D%3D"
    print(f"Loading search: {search_url}...")
    checkpoint("Search for playlist")
    page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(6000)

    # Find and click first playlist link
    checkpoint("Find playlist link")
    playlist_url = page.evaluate(r"""() => {
        const links = Array.from(document.querySelectorAll('a[href*="list="]'));
        for (const a of links) {
            const href = a.getAttribute('href');
            if (href && href.includes('/playlist?list=')) return href;
            if (href && href.includes('&list=')) {
                const m = href.match(/list=([^&]+)/);
                if (m) return '/playlist?list=' + m[1];
            }
        }
        return null;
    }""")

    if playlist_url:
        full_url = f"https://www.youtube.com{playlist_url}" if playlist_url.startswith("/") else playlist_url
        print(f"Found playlist: {full_url}")
        checkpoint("Navigate to playlist")
        page.goto(full_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(6000)
        # Scroll down to load more items
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3000)
    else:
        print("  No playlist found in search results.")
        return PlaylistResult()

    result = PlaylistResult()

    checkpoint("Extract video list")
    js_code = r"""(max) => {
        const lines = document.body.innerText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find playlist title (after "Play all")
        let playlistTitle = '';
        let i = 0;
        // Find "Play all" and title is a few lines before
        for (; i < lines.length; i++) {
            if (lines[i] === 'Play all') break;
        }
        // Title is near the start after nav
        for (let j = 0; j < i; j++) {
            if (lines[j].length > 5 && lines[j] !== 'Skip navigation' && lines[j] !== 'Sign in' &&
                lines[j] !== 'Home' && lines[j] !== 'Shorts' && lines[j] !== 'Subscriptions' &&
                lines[j] !== 'You') {
                playlistTitle = lines[j]; break;
            }
        }
        // Find second "Play all" (the one before video list)
        let startIdx = 0;
        let playAllCount = 0;
        for (let j = 0; j < lines.length; j++) {
            if (lines[j] === 'Play all') { playAllCount++; if (playAllCount === 2) { startIdx = j + 1; break; } }
        }
        if (playAllCount < 2) {
            // Fallback: use first Play all
            for (let j = 0; j < lines.length; j++) {
                if (lines[j] === 'Play all') { startIdx = j + 1; break; }
            }
        }
        i = startIdx;
        const videos = [];
        const durRe = /^\d{1,2}:\d{2}(:\d{2})?$/;
        const numRe = /^\d+$/;
        while (i < lines.length && videos.length < max) {
            // Expect index number
            if (!numRe.test(lines[i])) break;
            const idx = lines[i]; i++;
            // Optional duration
            let duration = '';
            if (i < lines.length && durRe.test(lines[i])) { duration = lines[i]; i++; }
            // Optional "Now playing"
            if (i < lines.length && lines[i] === 'Now playing') i++;
            // Title
            if (i >= lines.length) break;
            const title = lines[i]; i++;
            // Channel
            let channel = '';
            if (i < lines.length && lines[i] !== '•' && !numRe.test(lines[i])) {
                channel = lines[i]; i++;
            }
            // Skip "•"
            if (i < lines.length && lines[i] === '•') i++;
            // Views and age info
            let viewsInfo = '';
            if (i < lines.length && !numRe.test(lines[i]) && lines[i] !== 'Play all') {
                viewsInfo = lines[i]; i++;
            }
            videos.push({index: idx, title, channel, duration, viewsInfo});
        }
        return {playlistTitle, videos};
    }"""
    data = page.evaluate(js_code, request.max_results)

    result.playlist_title = data.get("playlistTitle", "")
    for vd in data.get("videos", []):
        v = VideoResult()
        v.index = vd.get("index", "")
        v.title = vd.get("title", "")
        v.channel = vd.get("channel", "")
        v.duration = vd.get("duration", "")
        v.views_info = vd.get("viewsInfo", "")
        result.videos.append(v)

    print(f"\n  Playlist: {result.playlist_title}")
    for v in result.videos:
        print(f"    {v.index}. [{v.duration}] {v.title} - {v.channel} ({v.views_info})")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("youtube_playlist")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = PlaylistRequest()
            result = youtube_playlist(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.videos)} videos")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
