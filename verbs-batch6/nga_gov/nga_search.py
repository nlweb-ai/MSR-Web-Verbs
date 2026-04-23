"""
Auto-generated Playwright script (Python)
National Gallery of Art – Artwork Search
Query: "Monet impressionism"
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
class ArtworkRequest:
    query: str = "Monet impressionism"
    max_results: int = 5


@dataclass
class Artwork:
    title: str = ""
    artist: str = ""
    date: str = ""
    medium: str = ""
    url: str = ""


@dataclass
class ArtworkResult:
    artworks: List[Artwork] = field(default_factory=list)


def nga_search(page: Page, request: ArtworkRequest) -> ArtworkResult:
    """Search NGA for artworks via Google site search."""
    print(f"  Query: {request.query}\n")

    from urllib.parse import quote_plus
    url = f"https://www.google.com/search?q=site%3Anga.gov+collection+{quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Google site search for NGA")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    checkpoint("Extract artwork listings from Google results")
    artworks_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();
        const h3s = document.querySelectorAll('h3');
        for (const h of h3s) {
            if (results.length >= maxResults) break;
            let text = h.innerText.trim();
            text = text.replace(/\s*[\|\u2013\u2014-]\s*NGA.*$/i, '').trim();
            text = text.replace(/\s*[\|\u2013\u2014-]\s*National Gallery.*$/i, '').trim();
            if (text.length < 3 || seen.has(text)) continue;

            let title = text, artist = '', date = '';
            // Try to extract artist from "Title by Artist" or "Artist - Title"
            const byMatch = text.match(/^(.+?)\s+by\s+(.+)$/i);
            if (byMatch) { title = byMatch[1]; artist = byMatch[2]; }

            // Extract year if present
            const yearMatch = text.match(/(\d{4})/);
            if (yearMatch) date = yearMatch[1];

            let url = '';
            const link = h.closest('a') || h.parentElement?.closest('a');
            if (link) url = link.href || '';

            seen.add(text);
            results.push({ title: title.slice(0, 120), artist: artist.slice(0, 60), date, medium: '', url });
        }
        return results;
    }""", request.max_results)

    artworks = [Artwork(**d) for d in artworks_data]
    result = ArtworkResult(artworks=artworks[:request.max_results])

    print("\n" + "=" * 60)
    print(f"NGA: {request.query}")
    print("=" * 60)
    for i, a in enumerate(result.artworks, 1):
        print(f"  {i}. {a.title}")
        if a.artist:
            print(f"     Artist: {a.artist}")
        if a.date:
            print(f"     Date:   {a.date}")
        if a.medium:
            print(f"     Medium: {a.medium}")
        if a.url:
            print(f"     URL:    {a.url}")
    print(f"\nTotal: {len(result.artworks)} artworks")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("nga_gov")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = nga_search(page, ArtworkRequest())
            print(f"\nReturned {len(result.artworks)} artworks")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
