import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class ApplePodcastsSearchRequest:
    query: str = "true crime"
    max_results: int = 5

@dataclass(frozen=True)
class ApplePodcast:
    podcast_name: str = ""
    publisher: str = ""
    url: str = ""
    artwork_url: str = ""

@dataclass(frozen=True)
class ApplePodcastsSearchResult:
    podcasts: list = None  # list[ApplePodcast]

# Search for podcasts on Apple Podcasts matching a query and extract
# podcast name, publisher, url, and artwork url.
def apple_podcasts_search(page: Page, request: ApplePodcastsSearchRequest) -> ApplePodcastsSearchResult:
    query = request.query
    max_results = request.max_results
    print(f"  Search query: {query}")
    print(f"  Max results: {max_results}\n")

    url = f"https://podcasts.apple.com/search?term={quote_plus(query)}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to Apple Podcasts search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    results = []

    # The search page has multiple <section> elements.
    # Section 1 (the "Shows" section) has <li> items with the pattern:
    #   line 0: podcast name
    #   line 1: podcast name (repeated)
    #   line 2: publisher
    # Each <li> also has an <a> linking to the podcast page and an <img> for artwork.
    sections = page.locator('section')
    shows_section = None
    for si in range(min(sections.count(), 5)):
        sec = sections.nth(si)
        li_items = sec.locator('li:has(a[href*="/podcast/"])')
        if li_items.count() >= 5:
            sample = li_items.first.inner_text(timeout=3000).strip()
            sample_lines = [l.strip() for l in sample.split("\n") if l.strip()]
            if len(sample_lines) >= 3 and sample_lines[2] not in ("Show", "Category"):
                shows_section = sec
                break

    def _extract_from_li(li):
        txt = li.inner_text(timeout=3000).strip()
        lines = [l.strip() for l in txt.split("\n") if l.strip()]
        podcast_name = lines[0] if len(lines) > 0 else "N/A"
        publisher = lines[2] if len(lines) > 2 else "N/A"
        link = li.locator('a[href*="/podcast/"]').first
        href = link.get_attribute("href", timeout=3000) or ""
        pod_url = href if href.startswith("http") else (f"https://podcasts.apple.com{href}" if href else "N/A")
        img = li.locator('img, source[srcset]').first
        artwork = ""
        if img.count() > 0:
            artwork = img.get_attribute("srcset", timeout=3000) or img.get_attribute("src", timeout=3000) or ""
            if artwork and "," in artwork:
                artwork = artwork.split(",")[0].strip().split(" ")[0]  # first srcset entry
        if not artwork:
            artwork = "N/A"
        return podcast_name, publisher, pod_url, artwork

    if shows_section:
        li_items = shows_section.locator('li:has(a[href*="/podcast/"])')
        count = li_items.count()
        print(f"  Found {count} podcast items in Shows section")
        for i in range(min(count, max_results)):
            li = li_items.nth(i)
            try:
                name, pub, pod_url, art = _extract_from_li(li)
                results.append(ApplePodcast(podcast_name=name, publisher=pub, url=pod_url, artwork_url=art))
            except Exception:
                continue

    # Fallback: use Top Results section if Shows section didn't work
    if not results:
        print("  Shows section not found, trying Top Results...")
        for si in range(min(sections.count(), 5)):
            sec = sections.nth(si)
            li_items = sec.locator('li:has(a[href*="/podcast/"])')
            if li_items.count() > 0:
                count = li_items.count()
                for i in range(min(count, max_results)):
                    li = li_items.nth(i)
                    try:
                        name, pub, pod_url, art = _extract_from_li(li)
                        if name != "N/A":
                            results.append(ApplePodcast(podcast_name=name, publisher=pub, url=pod_url, artwork_url=art))
                    except Exception:
                        continue
                if results:
                    break
        results = results[:max_results]

    print("=" * 60)
    print(f"Apple Podcasts - Search Results for \"{query}\"")
    print("=" * 60)
    for idx, p in enumerate(results, 1):
        print(f"\n{idx}. {p.podcast_name}")
        print(f"   Publisher: {p.publisher}")
        print(f"   URL: {p.url}")
        print(f"   Artwork: {p.artwork_url}")

    print(f"\nFound {len(results)} podcasts")

    return ApplePodcastsSearchResult(podcasts=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = apple_podcasts_search(page, ApplePodcastsSearchRequest())
        print(f"\nReturned {len(result.podcasts or [])} podcasts")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
