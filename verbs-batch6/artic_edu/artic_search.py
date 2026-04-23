"""
Auto-generated Playwright script (Python)
Art Institute of Chicago – Collection Search
Query: "Claude Monet"

Generated on: 2026-04-18T04:50:10.268Z
Recorded 2 browser interactions
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
class ArtworkRequest:
    query: str = "Claude Monet"
    max_artworks: int = 5


@dataclass
class Artwork:
    title: str = ""
    artist: str = ""
    date: str = ""
    medium: str = ""
    url: str = ""


@dataclass
class ArtworkResult:
    artworks: list = field(default_factory=list)


def artic_search(page: Page, request: ArtworkRequest) -> ArtworkResult:
    """Search Art Institute of Chicago collection using their public API."""
    print(f"  Query: {request.query}\n")

    # ── Use AIC public API (website has Cloudflare protection) ────────
    api_url = (
        f"https://api.artic.edu/api/v1/artworks/search"
        f"?q={quote_plus(request.query)}"
        f"&limit={request.max_artworks}"
        f"&fields=title,artist_display,date_display,medium_display,id"
    )
    print(f"Loading {api_url}...")
    checkpoint("Query AIC public API")
    page.goto(api_url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # ── Parse the JSON response ───────────────────────────────────────
    checkpoint("Parse API response")
    artworks_data = page.evaluate(r"""() => {
        try {
            const json = JSON.parse(document.body.innerText);
            if (!json.data) return [];
            return json.data.map(item => ({
                title: item.title || '',
                artist: item.artist_display || '',
                date: item.date_display || '',
                medium: item.medium_display || '',
                url: 'https://www.artic.edu/artworks/' + item.id,
            }));
        } catch (e) {
            return [];
        }
    }""")

    result = ArtworkResult(
        artworks=[Artwork(title=a['title'], artist=a['artist'], date=a['date'], medium=a['medium']) for a in artworks_data]
    )

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Art Institute of Chicago: {request.query}")
    print("=" * 60)
    for i, a in enumerate(artworks_data, 1):
        print(f"\n  {i}. {a['title']}")
        print(f"     Artist: {a['artist']}")
        print(f"     Date: {a['date']}")
        print(f"     Medium: {a['medium']}")
        print(f"     URL: {a['url']}")
    print(f"\n  Total: {len(result.artworks)} artworks")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("artic_edu")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = artic_search(page, ArtworkRequest())
            print(f"\nReturned {len(result.artworks)} artworks")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
