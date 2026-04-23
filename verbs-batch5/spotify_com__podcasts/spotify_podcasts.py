"""
Auto-generated Playwright script (Python)
Spotify – Search Podcasts
Query: "true crime"

Generated on: 2026-04-18T02:20:37.821Z
Recorded 6 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from urllib.parse import quote
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class SpotifyRequest:
    query: str = "true crime"
    max_podcasts: int = 5


@dataclass
class Podcast:
    name: str = ""
    publisher: str = ""
    description: str = ""
    rating: str = ""


@dataclass
class SpotifyResult:
    podcasts: list = field(default_factory=list)


def spotify_podcasts(page: Page, request: SpotifyRequest) -> SpotifyResult:
    """Search Spotify for podcasts."""
    print(f"  Query: {request.query}\n")

    # ── Search ────────────────────────────────────────────────────────
    search_url = f"https://open.spotify.com/search/{quote(request.query)}/podcasts"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to Spotify podcast search")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    # ── Extract podcast cards ─────────────────────────────────────────
    cards = page.evaluate(r"""(maxPodcasts) => {
        const cardEls = document.querySelectorAll('[data-testid*="card"]');
        const results = [];
        for (const card of cardEls) {
            if (results.length >= maxPodcasts) break;
            const link = card.querySelector('a[href*="/show/"]');
            if (!link) continue;
            const text = card.innerText.trim();
            const lines = text.split('\n').filter(l => l.trim());
            results.push({
                name: lines[0] || '',
                publisher: lines[1] || '',
                url: link.href,
            });
        }
        return results;
    }""", request.max_podcasts)

    # ── Visit each podcast page for details ───────────────────────────
    podcasts = []
    for card in cards:
        print(f"  Checking: {card['name']}...")
        checkpoint(f"Visit podcast: {card['name']}")
        page.goto(card['url'], wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

        detail = page.evaluate(r"""() => {
            const text = document.body.innerText;

            // Description: between "About\n" and ratings/episodes
            let desc = '';
            const aboutIdx = text.indexOf('About\n');
            if (aboutIdx >= 0) {
                const afterAbout = text.substring(aboutIdx + 6, aboutIdx + 600).trim();
                // Take text until "Show more" or rating pattern
                const endMatch = afterAbout.match(/(?:\n\d+\.\d+\n|… Show more|\nAll Episodes)/);
                desc = endMatch ? afterAbout.substring(0, endMatch.index).trim() : afterAbout.substring(0, 200).trim();
            }

            // Rating
            let rating = '';
            const ratingMatch = text.match(/(\d+\.\d+)\n\((\d[\d.]*K?)\)/);
            if (ratingMatch) rating = ratingMatch[1];

            return { description: desc, rating };
        }""")

        podcasts.append({
            'name': card['name'],
            'publisher': card['publisher'],
            'description': detail['description'],
            'rating': detail['rating'],
        })

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Spotify podcasts: {request.query}")
    print("=" * 60)
    for idx, p in enumerate(podcasts, 1):
        print(f"\n  {idx}. {p['name']}")
        print(f"     Publisher: {p['publisher']}")
        if p['rating']:
            print(f"     Rating: {p['rating']}")
        if p['description']:
            desc = p['description'][:120] + "..." if len(p['description']) > 120 else p['description']
            print(f"     Description: {desc}")

    return SpotifyResult(podcasts=[Podcast(**p) for p in podcasts])


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("spotify_podcasts")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = spotify_podcasts(page, SpotifyRequest())
            print(f"\nReturned {len(result.podcasts)} podcasts")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
