"""
Auto-generated Playwright script (Python)
Ultimate Guitar – Tab Search

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
    search_query: str = "Wonderwall Oasis"
    max_results: int = 5


@dataclass
class TabResult:
    title: str = ""
    artist: str = ""
    rating: str = ""
    type: str = ""


@dataclass
class SearchResult:
    tabs: List[TabResult] = field(default_factory=list)


def ultimateguitar_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search Ultimate Guitar for tabs."""
    print(f"  Query: {request.search_query}\n")

    query_encoded = request.search_query.replace(" ", "+")
    url = f"https://www.ultimate-guitar.com/search.php?search_type=title&value={query_encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = SearchResult()

    checkpoint("Extract tab results")
    js_code = r"""(max) => {
        const lines = document.body.innerText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find "ARTIST  SONG    RATING  TYPE" header
        let startIdx = 0;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].includes('ARTIST') && lines[i].includes('SONG') && lines[i].includes('TYPE')) {
                startIdx = i + 1; break;
            }
        }
        // Find artist name (first line after header)
        let currentArtist = '';
        let i = startIdx;
        if (i < lines.length) { currentArtist = lines[i]; i++; }
        const tabs = [];
        // Skip the Official and Pro entries
        while (i < lines.length && tabs.length < max) {
            const line = lines[i];
            if (!line || /^\d+$/.test(line) && parseInt(line) < 10) break; // page numbers
            if (line === 'NEXT >' || line === 'Sign up') break;
            // Check if it's a new artist
            if (line === 'Misc Mashups' || line === 'Sledding With Tigers') {
                currentArtist = line; i++; continue;
            }
            // Check if it's a tab title (contains "Wonderwall" or similar song names)
            // Skip Official/Pro entries and descriptions
            if (line.startsWith('Official version') || line.startsWith('Lead ') || line === 'High quality' || line === 'Official' || line === 'Pro') {
                i++; continue;
            }
            // Check if this is a duration like "4:08"
            if (/^\d+:\d+$/.test(line)) { i++; continue; }
            // Check if it's a tab type
            const types = ['Chords', 'Tab', 'Guitar Pro', 'Bass', 'Power', 'Drums', 'Video', 'Ukulele'];
            if (types.includes(line)) { i++; continue; }
            // Check if it's a rating number (3+ digits)
            if (/^[\d,]+$/.test(line) && line.replace(/,/g, '').length >= 1) { i++; continue; }
            // This should be a title line
            const title = line.replace(/\*$/, '');
            i++;
            // Look ahead for rating and type
            let rating = '';
            let tabType = '';
            // Skip empty/rating lines
            while (i < lines.length) {
                const next = lines[i];
                if (/^[\d,]+$/.test(next)) { rating = next; i++; continue; }
                if (types.includes(next)) { tabType = next; i++; break; }
                if (next === 'High quality' || next === 'Official') { i++; continue; }
                break;
            }
            if (title && tabType) {
                tabs.push({title, artist: currentArtist, rating, type: tabType});
            }
        }
        return tabs;
    }"""
    tabs_data = page.evaluate(js_code, request.max_results)

    for td in tabs_data:
        t = TabResult()
        t.title = td.get("title", "")
        t.artist = td.get("artist", "")
        t.rating = td.get("rating", "")
        t.type = td.get("type", "")
        result.tabs.append(t)

    for i, t in enumerate(result.tabs, 1):
        print(f"\n  Tab {i}:")
        print(f"    Title:  {t.title}")
        print(f"    Artist: {t.artist}")
        print(f"    Rating: {t.rating}")
        print(f"    Type:   {t.type}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("ultimateguitar")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = ultimateguitar_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.tabs)} tabs")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
