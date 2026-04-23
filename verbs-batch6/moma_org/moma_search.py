"""
Auto-generated Playwright script (Python)
MoMA – Collection Search
Query: "Andy Warhol"

Generated on: 2026-04-18T15:17:16.426Z
Recorded 2 browser interactions
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
class ArtRequest:
    query: str = "Andy Warhol"
    max_results: int = 5


@dataclass
class Artwork:
    title: str = ""
    artist: str = ""
    date: str = ""
    medium: str = ""
    url: str = ""


@dataclass
class ArtResult:
    artworks: List[Artwork] = field(default_factory=list)


def moma_search(page: Page, request: ArtRequest) -> ArtResult:
    """Search MoMA collection."""
    print(f"  Query: {request.query}\n")

    url = f"https://www.moma.org/collection/?q={request.query.replace(' ', '+')}&on_view=0"
    print(f"Loading {url}...")
    checkpoint("Navigate to MoMA collection search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(7000)

    checkpoint("Extract artwork listings")
    artworks_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();

        // MoMA structure: link text is "Artist\n\nTitle\n\nDate"
        // or "Image not available\n\nArtist\n\nTitle\n\nDate"
        const links = document.querySelectorAll('a[href*="/collection/works/"]');
        for (const a of links) {
            if (results.length >= maxResults) break;
            const href = a.getAttribute('href') || '';
            if (!/\/works\/\d+/.test(href)) continue;

            const text = a.innerText || '';
            // Split on double newlines (the actual separator)
            let parts = text.split(/\n\n/).map(s => s.trim()).filter(s => s.length > 0);
            
            // Skip "Image not available"
            if (parts[0] === 'Image not available') parts.shift();
            if (parts.length < 2) continue;

            let artist = parts[0];
            let title = parts[1];
            let date = parts.length > 2 ? parts[2] : '';

            // Dedup by href ID to avoid repeated entries
            const idM = href.match(/\/works\/(\d+)/);
            const key = idM ? idM[1] : title;
            if (seen.has(key)) continue;
            seen.add(key);

            if (/^(search|home|sign|filter|sort|show)/i.test(title)) continue;

            results.push({
                title: title.replace(/\n/g, ' ').slice(0, 100),
                artist: artist.slice(0, 80),
                date: date.slice(0, 30),
                medium: ''
            });
        }
        return results;
    }""", request.max_results)

    artworks = [Artwork(**d) for d in artworks_data]

    result = ArtResult(artworks=artworks[:request.max_results])

    print("\n" + "=" * 60)
    print(f"MoMA: {request.query}")
    print("=" * 60)
    for i, a in enumerate(result.artworks, 1):
        print(f"  {i}. {a.title}")
        if a.artist:
            print(f"     Artist: {a.artist}")
        if a.date:
            print(f"     Date:   {a.date}")
        if a.medium:
            print(f"     Medium: {a.medium}")
    print(f"\nTotal: {len(result.artworks)} artworks")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("moma_org")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = moma_search(page, ArtRequest())
            print(f"\nReturned {len(result.artworks)} artworks")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
