"""
Auto-generated Playwright script (Python)
Last.fm – Artist lookup

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re, urllib.parse
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ArtistLookupRequest:
    artist: str = "Radiohead"
    max_tracks: int = 5


@dataclass
class Track:
    name: str = ""
    listeners: str = ""


@dataclass
class ArtistLookupResult:
    artist_name: str = ""
    listeners: str = ""
    scrobbles: str = ""
    bio: str = ""
    top_tracks: List[Track] = field(default_factory=list)


def artist_lookup(page: Page, request: ArtistLookupRequest) -> ArtistLookupResult:
    """Look up an artist on Last.fm and extract profile info."""
    print(f"  Artist: {request.artist}")
    print(f"  Max tracks: {request.max_tracks}\n")

    checkpoint("Navigate to Last.fm artist page")
    slug = urllib.parse.quote(request.artist, safe="")
    page.goto(f"https://www.last.fm/music/{slug}", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract artist info")
    result = ArtistLookupResult()

    info = page.evaluate(
        r"""(maxTracks) => {
            const body = document.body.innerText;
            const lines = body.split('\n').map(l => l.trim()).filter(Boolean);

            // Artist name from h1
            const h1 = document.querySelector('h1');
            const artistName = h1 ? h1.textContent.trim() : '';

            // Listeners and Scrobbles
            let listeners = '', scrobbles = '';
            for (let i = 0; i < lines.length; i++) {
                if (lines[i] === 'Listeners' && i + 1 < lines.length) listeners = lines[i + 1];
                if (lines[i] === 'Scrobbles' && i + 1 < lines.length) scrobbles = lines[i + 1];
            }

            // Bio - find paragraph that starts with the artist name
            let bio = '';
            const bioMatch = body.match(new RegExp(artistName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\s+(?:are|is|was|were)\\s+[\\s\\S]{10,300}'));
            if (bioMatch) {
                bio = bioMatch[0].replace(/\s*…?\s*read more.*$/s, '').trim().slice(0, 300);
            }

            // Top tracks from table rows
            const trackRows = document.querySelectorAll('table.chartlist tr, tr.chartlist-row');
            const tracks = [];
            for (let i = 0; i < trackRows.length && tracks.length < maxTracks; i++) {
                const nameEl = trackRows[i].querySelector('.chartlist-name, td.chartlist-name a');
                const countEl = trackRows[i].querySelector('.chartlist-count-bar-value, .chartlist-count');
                if (nameEl) {
                    const link = nameEl.querySelector('a');
                    const name = link ? link.textContent.trim() : nameEl.textContent.trim();
                    const listenerCount = countEl ? countEl.textContent.replace(/listeners/i, '').trim() : '';
                    tracks.push({name, listeners: listenerCount});
                }
            }

            // Fallback: parse from innerText if table selectors failed
            if (tracks.length === 0) {
                let inTracks = false;
                for (let i = 0; i < lines.length; i++) {
                    if (lines[i] === 'Top Tracks' || lines[i].startsWith('Sorted by')) {
                        inTracks = true;
                        continue;
                    }
                    if (inTracks && lines[i] === 'View all tracks') break;
                    if (inTracks && lines[i].match(/^\d+$/)) {
                        // Rank number - next meaningful line is track name
                        // Then find listener count
                    }
                }
            }

            return {artist_name: artistName, listeners, scrobbles, bio, tracks};
        }""",
        request.max_tracks,
    )

    result.artist_name = info.get("artist_name", "")
    result.listeners = info.get("listeners", "")
    result.scrobbles = info.get("scrobbles", "")
    result.bio = info.get("bio", "")

    for t in info.get("tracks", []):
        track = Track()
        track.name = t.get("name", "")
        track.listeners = t.get("listeners", "")
        result.top_tracks.append(track)

    print(f"  Artist:    {result.artist_name}")
    print(f"  Listeners: {result.listeners}")
    print(f"  Scrobbles: {result.scrobbles}")
    print(f"  Bio:       {result.bio[:150]}...")
    print()
    for i, t in enumerate(result.top_tracks):
        print(f"  Track {i + 1}: {t.name} ({t.listeners})")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("lastfm")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = ArtistLookupRequest()
            result = artist_lookup(page, request)
            print(f"\n=== DONE ===")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
