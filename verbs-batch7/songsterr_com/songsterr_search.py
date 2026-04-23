"""
Auto-generated Playwright script (Python)
Songsterr – Tab Search

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
    search_query: str = "Stairway to Heaven Led Zeppelin"
    max_results: int = 5


@dataclass
class TabResult:
    song_title: str = ""
    artist: str = ""
    variant: str = ""


@dataclass
class SearchResult:
    tabs: List[TabResult] = field(default_factory=list)


def songsterr_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search Songsterr for guitar tabs."""
    print(f"  Query: {request.search_query}\n")

    # ── Navigate to search page ───────────────────────────────────────
    query_encoded = request.search_query.replace(" ", "+")
    url = f"https://www.songsterr.com/?pattern={query_encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = SearchResult()

    # ── Extract tab results via text parsing ──────────────────────────
    checkpoint("Extract tab results")
    js_code = r"""(max) => {
        const body = document.body.innerText;
        const lines = body.split('\n').map(l => l.trim()).filter(l => l.length > 0);

        // Find search results - they start after "SIGN IN" nav
        let startIdx = 0;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === 'SIGN IN') { startIdx = i + 1; break; }
        }
        // Skip the search input text
        if (startIdx < lines.length && lines[startIdx].includes('Search tabs')) startIdx++;

        const tabs = [];
        let i = startIdx;
        while (i < lines.length && tabs.length < max) {
            const title = lines[i];
            // Stop at tab viewer content
            if (title.startsWith('Songsterr Plus') || title.startsWith('REVISION') ||
                title === 'ORIGINAL' || title === 'SYNTH') break;
            // Skip promotional lines
            if (title === "Can't find the tab you need?" || title === 'Transcribe one with Songsterr AI') {
                i++; continue;
            }

            i++;
            if (i >= lines.length) break;
            const artist = lines[i];
            i++;

            if (title && artist && !title.startsWith('Songsterr')) {
                tabs.push({title, artist, variant: ''});
            }
        }
        return tabs;
    }"""
    tabs_data = page.evaluate(js_code, request.max_results)

    for td in tabs_data:
        tab = TabResult()
        tab.song_title = td.get("title", "")
        tab.artist = td.get("artist", "")
        tab.variant = td.get("variant", "")
        result.tabs.append(tab)

    # ── Print results ─────────────────────────────────────────────────
    for i, t in enumerate(result.tabs, 1):
        print(f"\n  Tab {i}:")
        print(f"    Song:    {t.song_title}")
        print(f"    Artist:  {t.artist}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("songsterr")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = songsterr_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.tabs)} tabs")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
