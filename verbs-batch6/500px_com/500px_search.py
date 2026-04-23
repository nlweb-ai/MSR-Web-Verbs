"""
Auto-generated Playwright script (Python)
500px – Photo Search
Query: "street photography"

Generated on: 2026-04-18T04:23:45.168Z
Recorded 2 browser interactions

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
class PhotoSearchRequest:
    query: str = "street photography"
    max_results: int = 5


@dataclass
class Photo:
    title: str = ""
    photographer: str = ""
    likes: str = ""
    photo_url: str = ""


@dataclass
class PhotoSearchResult:
    photos: list = field(default_factory=list)


def photo_search_500px(page: Page, request: PhotoSearchRequest) -> PhotoSearchResult:
    """Search 500px for photos matching a query."""
    print(f"  Query: {request.query}\n")

    # ── Navigate to search ────────────────────────────────────────────
    search_url = f"https://500px.com/search?q={quote_plus(request.query)}&type=photos"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to 500px search")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Extract photos ────────────────────────────────────────────────
    photos = page.evaluate(r"""(maxResults) => {
        const results = [];
        // 500px photo grid items
        const links = document.querySelectorAll('a[href*="/photo/"]');
        const seen = new Set();
        for (const link of links) {
            if (results.length >= maxResults) break;
            const href = link.getAttribute('href');
            if (!href || seen.has(href)) continue;
            seen.add(href);
            const photoUrl = href.startsWith('http') ? href : 'https://500px.com' + href;

            // Try to find title from alt text of img or aria-label
            const img = link.querySelector('img');
            let title = '';
            if (img) {
                title = img.getAttribute('alt') || img.getAttribute('title') || '';
            }
            if (!title) {
                title = link.getAttribute('aria-label') || link.getAttribute('title') || '';
            }

            // Find photographer and likes from nearby text
            const container = link.closest('div[class]') || link.parentElement;
            let photographer = '';
            let likes = '';
            if (container) {
                // Look for photographer name link
                const userLinks = container.querySelectorAll('a[href*="/p/"], a[href*="/user/"]');
                for (const ul of userLinks) {
                    const text = ul.innerText.trim();
                    if (text && text.length > 0 && text.length < 100) {
                        photographer = text;
                        break;
                    }
                }
                // Look for likes/pulse count
                const allText = container.innerText || '';
                const likeMatch = allText.match(/(\d+)\s*(likes?|pulses?|♥|❤)/i);
                if (likeMatch) {
                    likes = likeMatch[1];
                } else {
                    // Try finding a small number near a heart icon
                    const spans = container.querySelectorAll('span');
                    for (const sp of spans) {
                        const t = sp.innerText.trim();
                        if (/^\d+$/.test(t) && parseInt(t) < 100000) {
                            likes = t;
                            break;
                        }
                    }
                }
            }

            if (title || photographer) {
                results.push({
                    title: title || 'Untitled',
                    photographer: photographer || 'Unknown',
                    likes: likes || '0',
                    photo_url: photoUrl,
                });
            }
        }
        return results;
    }""", request.max_results)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"500px Photos: {request.query}")
    print("=" * 60)
    for idx, p in enumerate(photos, 1):
        print(f"\n  {idx}. {p['title']}")
        print(f"     Photographer: {p['photographer']}")
        print(f"     Likes: {p['likes']}")
        print(f"     URL: {p['photo_url']}")

    result_photos = [Photo(**p) for p in photos]
    print(f"\nFound {len(result_photos)} photos")
    return PhotoSearchResult(photos=result_photos)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("500px_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = photo_search_500px(page, PhotoSearchRequest())
            print(f"\nReturned {len(result.photos)} photos")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
