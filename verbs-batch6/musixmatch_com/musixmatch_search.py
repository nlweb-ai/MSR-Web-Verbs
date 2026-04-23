"""
Auto-generated Playwright script (Python)
Musixmatch – Lyrics Search
Query: "Bohemian Rhapsody"
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class SongRequest:
    query: str = "Bohemian Rhapsody"
    max_results: int = 5


@dataclass
class Song:
    title: str = ""
    artist: str = ""
    album: str = ""
    url: str = ""


@dataclass
class SongResult:
    songs: List[Song] = field(default_factory=list)


def musixmatch_search(page: Page, request: SongRequest) -> SongResult:
    """Search Musixmatch for song lyrics via Google site search."""
    print(f"  Query: {request.query}\n")

    from urllib.parse import quote_plus
    url = f"https://www.google.com/search?q=site%3Amusixmatch.com+{quote_plus(request.query)}+lyrics"
    print(f"Loading {url}...")
    checkpoint("Navigate to Google site search for Musixmatch")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    checkpoint("Extract song listings from Google results")
    songs_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();
        const h3s = document.querySelectorAll('h3');
        for (const h of h3s) {
            if (results.length >= maxResults) break;
            let text = h.innerText.trim();
            // Clean up " - Musixmatch" or " | Musixmatch" suffixes
            text = text.replace(/\s*[\|\u2013\u2014-]\s*Musixmatch.*$/i, '').trim();
            if (text.length < 3 || seen.has(text)) continue;

            // Try to split "Title - Artist" or "Artist - Title"
            let title = text, artist = '';
            const dashMatch = text.match(/^(.+?)\s*[\u2013\u2014-]\s*(.+)$/);
            if (dashMatch) {
                title = dashMatch[1].trim();
                artist = dashMatch[2].trim();
                // If title starts with "Lyrics", swap
                if (/^lyrics\b/i.test(title)) {
                    title = title.replace(/^lyrics\s*/i, '').trim();
                }
            }

            // Get URL from parent link
            let url = '';
            const link = h.closest('a') || h.parentElement?.closest('a');
            if (link) url = link.href || '';

            seen.add(text);
            results.push({ title: title.slice(0, 100), artist: artist.slice(0, 60), album: '', url });
        }
        return results;
    }""", request.max_results)

    songs = [Song(**d) for d in songs_data]
    result = SongResult(songs=songs[:request.max_results])

    print("\n" + "=" * 60)
    print(f"Musixmatch: {request.query}")
    print("=" * 60)
    for i, s in enumerate(result.songs, 1):
        print(f"  {i}. {s.title}")
        if s.artist:
            print(f"     Artist: {s.artist}")
        if s.album:
            print(f"     Album:  {s.album}")
        if s.url:
            print(f"     URL:    {s.url}")
    print(f"\nTotal: {len(result.songs)} songs")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("musixmatch_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = musixmatch_search(page, SongRequest())
            print(f"\nReturned {len(result.songs)} songs")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
