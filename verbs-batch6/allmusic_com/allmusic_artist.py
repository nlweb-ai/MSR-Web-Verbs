"""
Auto-generated Playwright script (Python)
AllMusic – Artist Info
Artist: "Miles Davis"

Generated on: 2026-04-18T04:41:48.244Z
Recorded 3 browser interactions
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
class ArtistRequest:
    artist: str = "Miles Davis"
    max_albums: int = 5


@dataclass
class Album:
    name: str = ""
    year: str = ""
    rating: str = ""


@dataclass
class ArtistResult:
    artist_name: str = ""
    active_years: str = ""
    genres: str = ""
    bio_summary: str = ""
    albums: list = field(default_factory=list)


def allmusic_artist(page: Page, request: ArtistRequest) -> ArtistResult:
    """Search AllMusic for artist info and top albums."""
    print(f"  Artist: {request.artist}\n")

    # ── Step 1: Go to AllMusic and search ─────────────────────────────
    print("Loading https://www.allmusic.com ...")
    checkpoint("Navigate to AllMusic homepage")
    page.goto("https://www.allmusic.com", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # Type into search box and submit
    search_input = page.locator("input.siteSearchInput")
    search_input.click()
    page.wait_for_timeout(500)
    search_input.press("Control+a")
    search_input.type(request.artist, delay=50)
    page.wait_for_timeout(500)
    search_input.press("Enter")
    page.wait_for_timeout(5000)

    # ── Step 2: Click first artist result ─────────────────────────────
    checkpoint("Click first artist result")
    artist_links = page.evaluate(r"""() => {
        const links = document.querySelectorAll('a[href*="/artist/"]');
        for (const a of links) {
            const text = a.innerText.trim();
            if (text.length > 1 && text.length < 100) {
                return a.href;
            }
        }
        return null;
    }""")

    if not artist_links:
        print("No artist results found.")
        return ArtistResult(artist_name=request.artist)

    page.goto(artist_links, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Step 3: Extract artist info from artist page ──────────────────
    checkpoint("Extract artist details")
    info = page.evaluate(r"""() => {
        const bodyText = document.body.innerText;

        // Artist name
        const h1 = document.querySelector('h1');
        const name = h1 ? h1.innerText.trim() : '';

        // Active years
        const activeMatch = bodyText.match(/Active\s*\n\s*(\S[^\n]*)/);
        const active = activeMatch ? activeMatch[1].trim() : '';

        // Genre
        const genreMatch = bodyText.match(/Genre\s*\n\s*(\S[^\n]*)/);
        const genre = genreMatch ? genreMatch[1].trim() : '';

        // Biography summary - first long paragraph
        const bioMatch = bodyText.match(/Biography by [^\n]+\n\n([\s\S]+?)(?:\n\nBorn|\n\n)/);
        let bio = '';
        if (bioMatch) {
            bio = bioMatch[1].trim().slice(0, 500);
        } else {
            const paras = document.querySelectorAll('p');
            for (const p of paras) {
                const t = p.innerText.trim();
                if (t.length > 100 && !t.includes('Advertising') && !t.includes('ASKING')) {
                    bio = t.slice(0, 500);
                    break;
                }
            }
        }

        return { name, active, genre, bio };
    }""")

    # ── Step 4: Click discography tab and extract top albums ────────
    checkpoint("Click Full Discography link")
    disc_link = page.locator("text=Full Discography").first
    if disc_link.count() > 0:
        disc_link.click()
        page.wait_for_timeout(5000)
    else:
        disc_tab = page.locator('[id="discographyTab"], [data-subtype="discography"]').first
        if disc_tab.count() > 0:
            disc_tab.click()
            page.wait_for_timeout(5000)

    albums_data = page.evaluate(r"""(maxAlbums) => {
        const results = [];
        const rows = document.querySelectorAll('table tbody tr');
        for (const row of rows) {
            if (results.length >= maxAlbums) break;

            // Album name and URL
            const titleLink = row.querySelector('td.meta a[href*="/album/"]');
            if (!titleLink) continue;
            const albumName = titleLink.innerText.trim();
            if (!albumName) continue;

            // Year
            const yearCell = row.querySelector('td.year');
            const year = yearCell ? yearCell.innerText.trim() : '';

            // AllMusic rating - class like "ratingAllmusic8" -> 8
            const ratingEl = row.querySelector('div[class*="ratingAllmusic"]');
            let rating = '';
            if (ratingEl) {
                const match = ratingEl.className.match(/ratingAllmusic(\d+)/);
                if (match) rating = match[1];
            }

            results.push({ name: albumName, year, rating });
        }
        return results;
    }""", request.max_albums)

    # ── Print results ─────────────────────────────────────────────────
    result = ArtistResult(
        artist_name=info.get("name", request.artist),
        active_years=info.get("active", ""),
        genres=info.get("genre", ""),
        bio_summary=info.get("bio", ""),
        albums=[Album(name=a["name"], year=a["year"], rating=a["rating"]) for a in albums_data],
    )

    print("\n" + "=" * 60)
    print(f"AllMusic: {result.artist_name}")
    print("=" * 60)
    print(f"  Active Years: {result.active_years}")
    print(f"  Genres: {result.genres}")
    print(f"  Bio: {result.bio_summary}")
    print(f"\n  Top Albums:")
    for i, album in enumerate(result.albums, 1):
        rating_str = f" (Rating: {album.rating}/10)" if album.rating else ""
        print(f"    {i}. {album.name} ({album.year}){rating_str}")
    print(f"\nTotal: {len(result.albums)} albums")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("allmusic_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = allmusic_artist(page, ArtistRequest())
            print(f"\nReturned info for {result.artist_name}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
