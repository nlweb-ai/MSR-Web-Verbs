"""
Auto-generated Playwright script (Python)
Met Museum – Collection Search
Query: "impressionism"

Generated on: 2026-04-18T15:16:00.562Z
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
    query: str = "impressionism"
    max_results: int = 5


@dataclass
class Artwork:
    title: str = ""
    artist: str = ""
    date: str = ""
    medium: str = ""
    image_url: str = ""


@dataclass
class ArtResult:
    artworks: List[Artwork] = field(default_factory=list)


def metmuseum_search(page: Page, request: ArtRequest) -> ArtResult:
    """Search Met Museum collection."""
    print(f"  Query: {request.query}\n")

    # Use the collection search URL (not the hash-based search-results URL)
    from urllib.parse import quote_plus
    url = f"https://www.metmuseum.org/art/collection/search?q={quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Met Museum collection search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(7000)

    # Scroll to load content
    for _ in range(3):
        page.evaluate("window.scrollBy(0, 600)")
        page.wait_for_timeout(800)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    checkpoint("Extract artwork listings")
    artworks_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();

        // Grid items are <figure class="collection-object"> with innerText "Title\nArtist\nDate"
        const figures = document.querySelectorAll('figure[class*="collectionObject"], figure.collection-object');
        for (const fig of figures) {
            if (results.length >= maxResults) break;
            const text = fig.innerText || '';
            const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 1);
            if (lines.length === 0) continue;

            let title = lines[0];
            if (seen.has(title)) continue;
            if (/^(search|home|sign|filter|sort|show)/i.test(title)) continue;
            seen.add(title);

            let artist = lines.length > 1 ? lines[1] : '';
            let date = lines.length > 2 ? lines[2] : '';

            // Get URL from link inside figure
            let url = '';
            const a = fig.querySelector('a');
            if (a) {
                const href = a.getAttribute('href') || '';
                url = href.startsWith('/') ? 'https://www.metmuseum.org' + href : href;
            }

            results.push({ title: title.slice(0, 100), artist: artist.slice(0, 80), date, medium: '' });
        }

        // Fallback: links with numeric collection IDs
        if (results.length === 0) {
            const links = document.querySelectorAll('a[href*="/art/collection/search/"]');
            for (const a of links) {
                if (results.length >= maxResults) break;
                const href = a.getAttribute('href') || '';
                if (!/\/search\/\d+/.test(href)) continue;
                const t = a.innerText.trim().split('\n')[0].trim();
                if (t.length < 4 || seen.has(t)) continue;
                seen.add(t);
                results.push({ title: t.slice(0, 100), artist: '', date: '', medium: '' });
            }
        }
        return results;
    }""", request.max_results)

    artworks = [Artwork(**d) for d in artworks_data]

    result = ArtResult(artworks=artworks[:request.max_results])

    print("\n" + "=" * 60)
    print(f"Met Museum: {request.query}")
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
    profile_dir = get_temp_profile_dir("metmuseum_org")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = metmuseum_search(page, ArtRequest())
            print(f"\nReturned {len(result.artworks)} artworks")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
