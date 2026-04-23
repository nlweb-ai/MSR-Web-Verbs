import re
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class FlickrSearchRequest:
    query: str = "northern lights"
    max_results: int = 5

@dataclass(frozen=True)
class FlickrPhoto:
    title: str = ""
    photographer: str = ""
    url: str = ""
    image_url: str = ""

@dataclass(frozen=True)
class FlickrSearchResult:
    photos: list = None  # list[FlickrPhoto]

# Search for photos on flickr.com matching a query and extract photo
# titles, photographer names, photo urls, and image urls.
def flickr_search(page: Page, request: FlickrSearchRequest) -> FlickrSearchResult:
    query = request.query
    max_results = request.max_results
    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    encoded_query = quote_plus(query)
    url = f"https://www.flickr.com/search/?text={encoded_query}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to Flickr search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    results = []

    # Try structured extraction via photo card divs.
    # Flickr renders each photo as a <div class="photo-list-photo-view"> with
    # a background-image style for the thumbnail and child <a> links.
    card_divs = page.locator('div.photo-list-photo-view')
    count = card_divs.count()
    print(f"  Found {count} photo card divs")

    seen_photo_ids = set()

    if count > 0:
        for i in range(count):
            if len(results) >= max_results:
                break
            card = card_divs.nth(i)
            try:
                # Get the main photo link (href matching /photos/{user}/{id})
                main_link = card.locator('a.overlay, a.title').first
                if main_link.count() == 0:
                    continue
                href = main_link.get_attribute("href", timeout=2000) or ""
                # Only accept links with a numeric photo ID
                id_match = re.search(r'/photos/([^/]+)/(\d+)', href)
                if not id_match:
                    continue
                photo_id = id_match.group(2)
                if photo_id in seen_photo_ids:
                    continue
                seen_photo_ids.add(photo_id)

                photo_url = href if href.startswith("http") else f"https://www.flickr.com{href}"

                # Title from a.title link text
                title_el = card.locator('a.title')
                title = title_el.inner_text(timeout=2000).strip() if title_el.count() > 0 else ""
                if not title:
                    # Fallback: aria-label on overlay link (e.g. "Northern lights by jaytee27")
                    overlay = card.locator('a.overlay')
                    if overlay.count() > 0:
                        aria = overlay.get_attribute("aria-label", timeout=2000) or ""
                        # Strip " by username" suffix
                        title = re.sub(r'\s+by\s+\S+$', '', aria).strip()
                if not title:
                    title = "N/A"

                # Photographer from a.attribution link text
                attr_el = card.locator('a.attribution')
                photographer = ""
                if attr_el.count() > 0:
                    photographer = attr_el.inner_text(timeout=2000).strip()
                    # Remove "by " prefix
                    photographer = re.sub(r'^by\s+', '', photographer, flags=re.I).strip()
                if not photographer:
                    photographer = id_match.group(1)

                # Image URL from <img> inside the card
                image_url = "N/A"
                img = card.locator('img').first
                if img.count() > 0:
                    src = img.get_attribute("src", timeout=2000) or ""
                    if src:
                        image_url = src if src.startswith("http") else f"https:{src}"

                results.append(FlickrPhoto(
                    title=title,
                    photographer=photographer,
                    url=photo_url,
                    image_url=image_url,
                ))
            except Exception:
                continue

    # Fallback: look for any links to /photos/{user}/{id} in the page
    if not results:
        print("  Primary selectors missed, trying broad link scan...")
        all_photo_links = page.locator('a[href*="/photos/"]')
        link_count = all_photo_links.count()
        for i in range(min(link_count, max_results * 5)):
            if len(results) >= max_results:
                break
            a = all_photo_links.nth(i)
            try:
                href = a.get_attribute("href", timeout=2000) or ""
                id_match = re.search(r'/photos/([^/]+)/(\d+)', href)
                if not id_match:
                    continue
                photo_id = id_match.group(2)
                if photo_id in seen_photo_ids:
                    continue
                seen_photo_ids.add(photo_id)
                photo_url = href if href.startswith("http") else f"https://www.flickr.com{href}"
                title = a.get_attribute("title", timeout=2000) or a.inner_text(timeout=2000).strip() or "N/A"
                photographer = id_match.group(1)

                results.append(FlickrPhoto(
                    title=title,
                    photographer=photographer,
                    url=photo_url,
                    image_url="N/A",
                ))
            except Exception:
                continue

    print("=" * 60)
    print(f"Flickr – Search Results for \"{query}\"")
    print("=" * 60)
    for idx, p in enumerate(results, 1):
        print(f"\n{idx}. {p.title}")
        print(f"   Photographer: {p.photographer}")
        print(f"   URL: {p.url}")
        print(f"   Image: {p.image_url}")

    print(f"\nFound {len(results)} photos")

    return FlickrSearchResult(photos=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = flickr_search(page, FlickrSearchRequest())
        print(f"\nReturned {len(result.photos or [])} photos")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
