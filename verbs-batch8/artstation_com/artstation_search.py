"""
Auto-generated Playwright script (Python)
ArtStation – Search Artwork
Query: "concept art"

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ArtStationRequest:
    search_query: str = "concept art"
    max_results: int = 5


@dataclass
class Artwork:
    title: str = ""
    artist_name: str = ""
    medium: str = ""
    num_likes: str = ""
    num_views: str = ""
    tags: str = ""


@dataclass
class ArtStationResult:
    artworks: list = field(default_factory=list)


def artstation_search(page: Page, request: ArtStationRequest) -> ArtStationResult:
    """Search artstation.com for artwork."""
    print(f"  Query: {request.search_query}\n")

    # ── Search ────────────────────────────────────────────────────────
    search_url = f"https://www.artstation.com/search?query={quote_plus(request.search_query)}&sort_by=relevance"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to ArtStation search")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)

    # ── Extract artworks ──────────────────────────────────────────────
    raw_artworks = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();
        
        // ArtStation uses data attributes and image cards
        // Try multiple strategies
        
        // Strategy 1: find project links
        const links = document.querySelectorAll('a[href*="/artwork/"], a[href*="/projects/"]');
        for (const a of links) {
            if (results.length >= maxResults) break;
            const href = a.getAttribute('href') || '';
            if (seen.has(href)) continue;
            seen.add(href);
            
            // Get the card container
            const card = a.closest('[class]') || a;
            const text = card.innerText.trim();
            const lines = text.split('\n').filter(l => l.trim());
            
            let title = '';
            let artist = '';
            // Title is often in aria-label or the link text
            const ariaLabel = a.getAttribute('aria-label') || a.getAttribute('title') || '';
            if (ariaLabel.length > 3) {
                title = ariaLabel;
            } else if (lines.length > 0) {
                title = lines[0];
            }
            if (lines.length > 1) artist = lines[1];
            
            // Get likes from nearby elements
            let likes = '';
            const likesEl = card.querySelector('[class*="like"]');
            if (likesEl) likes = likesEl.innerText.trim();
            
            if (title.length > 2) {
                results.push({
                    title, artist_name: artist, medium: '', num_likes: likes,
                    num_views: '0', tags: '',
                });
            }
        }
        
        // Strategy 2: if nothing found, look for image containers with overlay text
        if (results.length === 0) {
            const imgs = document.querySelectorAll('img[alt]');
            for (const img of imgs) {
                if (results.length >= maxResults) break;
                const alt = img.getAttribute('alt') || '';
                if (alt.length < 5) continue;
                if (seen.has(alt)) continue;
                seen.add(alt);
                
                const parent = img.closest('a, div');
                const parentText = parent ? parent.innerText.trim() : '';
                
                results.push({
                    title: alt, artist_name: parentText.split('\n').pop() || '',
                    medium: '', num_likes: '0', num_views: '0', tags: '',
                });
            }
        }
        
        return results;
    }""", request.max_results)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"ArtStation: {request.search_query}")
    print("=" * 60)
    for idx, a in enumerate(raw_artworks, 1):
        print(f"\n  {idx}. {a['title']}")
        print(f"     Artist: {a['artist_name']}")
        if a['medium']:
            print(f"     Medium: {a['medium']}")
        print(f"     Likes: {a['num_likes']}  Views: {a['num_views']}")
        if a['tags']:
            print(f"     Tags: {a['tags']}")

    artworks = [Artwork(**a) for a in raw_artworks]
    return ArtStationResult(artworks=artworks)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("artstation_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = artstation_search(page, ArtStationRequest())
            print(f"\nReturned {len(result.artworks)} artworks")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
