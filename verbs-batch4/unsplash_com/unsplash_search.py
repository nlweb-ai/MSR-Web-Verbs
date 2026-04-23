"""
Unsplash – Photo Search verb
Search Unsplash for photos and extract listings with photographer, description, and likes.
"""

import os
import re
from dataclasses import dataclass
from urllib.parse import quote as url_quote
from playwright.sync_api import Page, sync_playwright

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

# ── Types ─────────────────────────────────────────────────────────────────────

@dataclass
class UnsplashSearchRequest:
    search_term: str    # e.g. "mountain landscape"
    max_results: int    # number of photos to extract

@dataclass
class UnsplashPhoto:
    photographer_name: str  # name of the photographer
    description: str        # alt text or description of the photo
    num_likes: str          # number of likes (as string, or "N/A")

@dataclass
class UnsplashSearchResult:
    photos: list  # list of UnsplashPhoto

# ── Verb ──────────────────────────────────────────────────────────────────────

def unsplash_search(page: Page, request: UnsplashSearchRequest) -> UnsplashSearchResult:
    """
    Search Unsplash for photos and extract listings.

    Args:
        page: Playwright page.
        request: UnsplashSearchRequest with search_term and max_results.

    Returns:
        UnsplashSearchResult containing a list of UnsplashPhoto.
    """
    search_url = f"https://unsplash.com/s/photos/{url_quote(request.search_term.replace(' ', '-'))}"
    print(f"Loading {search_url}...")
    page.goto(search_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)
    print(f"  Loaded: {page.url}")
    checkpoint("Loaded Unsplash search page")

    # Dismiss cookie banners
    for selector in [
        'button:has-text("Accept")',
        'button:has-text("Got it")',
        'button:has-text("Accept & close")',
    ]:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=1500):
                btn.click()
                page.wait_for_timeout(500)
                break
        except Exception:
            pass

    # Extract photos via figure elements
    print(f"Extracting up to {request.max_results} photos...")

    photo_figures = page.locator('figure[itemprop="image"], figure[data-testid*="photo"], div[data-test*="photo"]')
    count = photo_figures.count()
    print(f"  Found {count} photo figures")

    if count == 0:
        photo_figures = page.locator('[data-testid="masonry-grid-count"] figure, [class*="MasonryGrid"] figure')
        count = photo_figures.count()
        print(f"  Fallback masonry: found {count} figures")

    if count == 0:
        photo_figures = page.locator('figure:has(img[src*="unsplash"])')
        count = photo_figures.count()
        print(f"  Broad fallback: found {count} figures")

    results = []
    seen = set()
    for i in range(count):
        if len(results) >= request.max_results:
            break
        fig = photo_figures.nth(i)
        try:
            # Photo description / alt text
            description = "N/A"
            try:
                img_el = fig.locator('img').first
                description = img_el.get_attribute("alt", timeout=2000) or "N/A"
                description = description.strip()
            except Exception:
                pass
            if description == "N/A":
                try:
                    title_link = fig.locator('a[itemprop="contentUrl"]').first
                    description = title_link.get_attribute("title", timeout=2000) or "N/A"
                except Exception:
                    pass

            if description == "N/A":
                continue

            # Photographer name
            photographer = "N/A"
            try:
                user_data = fig.evaluate("""el => {
                    const links = el.querySelectorAll('a[href*="/@"]');
                    for (const a of links) {
                        const text = a.innerText.trim();
                        if (text) return text;
                        const m = a.href.match(/@([^/?]+)/);
                        if (m) return m[1];
                    }
                    return null;
                }""")
                if user_data:
                    photographer = user_data
            except Exception:
                pass

            key = (photographer.lower(), description[:50].lower())
            if key in seen:
                continue
            seen.add(key)

            # Number of likes
            num_likes = "N/A"
            try:
                like_data = fig.evaluate("""el => {
                    const buttons = el.querySelectorAll('button');
                    for (const btn of buttons) {
                        const text = btn.innerText.trim();
                        if (/^\\d+$/.test(text)) return text;
                    }
                    for (const btn of buttons) {
                        const label = btn.getAttribute('aria-label') || '';
                        const m = label.match(/(\\d[\\d,]*)/);
                        if (m && /like/i.test(label)) return m[1];
                    }
                    return null;
                }""")
                if like_data:
                    num_likes = like_data
            except Exception:
                pass

            results.append(UnsplashPhoto(
                photographer_name=photographer,
                description=description,
                num_likes=num_likes,
            ))
        except Exception:
            continue

    # Fallback: extract from img alt attributes directly
    if not results:
        print("  Figure extraction failed, trying img alt fallback...")
        imgs = page.locator('img[src*="unsplash.com/photos"], img[srcset*="unsplash"]')
        img_count = imgs.count()
        for i in range(img_count):
            if len(results) >= request.max_results:
                break
            try:
                alt = imgs.nth(i).get_attribute("alt", timeout=1000) or ""
                if alt and len(alt) > 5:
                    results.append(UnsplashPhoto(
                        photographer_name="N/A",
                        description=alt.strip(),
                        num_likes="N/A",
                    ))
            except Exception:
                pass

    checkpoint("Extracted photo results")
    print(f'\nFound {len(results)} photos for "{request.search_term}":')
    for i, p in enumerate(results, 1):
        print(f"  {i}. Photographer: {p.photographer_name}")
        print(f"     Description: {p.description[:80]}")
        print(f"     Likes: {p.num_likes}")

    return UnsplashSearchResult(photos=results)

# ── Test ──────────────────────────────────────────────────────────────────────

def test_func():

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()

        request = UnsplashSearchRequest(search_term="mountain landscape", max_results=5)
        result = unsplash_search(page, request)
        print(f"\nTotal photos found: {len(result.photos)}")

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
