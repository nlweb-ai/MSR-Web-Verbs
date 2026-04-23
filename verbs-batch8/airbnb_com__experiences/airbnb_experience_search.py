"""
Airbnb Experiences – Search experiences by city

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ExperienceSearchRequest:
    city: str = "Tokyo, Japan"
    max_results: int = 5


@dataclass
class ExperienceItem:
    title: str = ""
    host_name: str = ""
    duration: str = ""
    price_per_person: str = ""
    rating: str = ""
    num_reviews: str = ""


@dataclass
class ExperienceSearchResult:
    items: List[ExperienceItem] = field(default_factory=list)


# Search for Airbnb Experiences in a given city and extract listing details.
def airbnb_experience_search(page: Page, request: ExperienceSearchRequest) -> ExperienceSearchResult:
    """Search Airbnb Experiences for a city and extract listings."""
    print(f"  City: {request.city}\n")

    # ── Navigate to Airbnb Experiences ─────────────────────────────────
    encoded = quote_plus(request.city)
    url = f"https://www.airbnb.com/s/{encoded}/experiences"
    print(f"Loading {url}...")
    checkpoint("Navigate to Airbnb Experiences")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = ExperienceSearchResult()

    # ── Extract experience listings ───────────────────────────────────
    checkpoint("Extract experience listings")
    js_code = """(max) => {
        const items = [];
        const seen = new Set();

        const allLinks = document.querySelectorAll('a[href*="/experiences/"]');
        for (const a of allLinks) {
            if (items.length >= max) break;
            // Walk up to the card container
            let card = a.closest('[itemprop="itemListElement"]');
            if (!card) card = a.closest('[data-testid]');
            if (!card) {
                // Walk up a few levels to find a reasonable card
                let el = a;
                for (let i = 0; i < 6 && el.parentElement; i++) el = el.parentElement;
                card = el;
            }
            if (!card || seen.has(card)) continue;
            seen.add(card);

            const text = card.innerText.trim();
            const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            if (lines.length < 2) continue;

            // Title: use aria-label on the link, or the longest non-badge line
            let title = '';
            const ariaLabel = a.getAttribute('aria-label');
            if (ariaLabel && ariaLabel.length > 5) {
                title = ariaLabel;
            } else {
                // Skip short badge words like "Popular", "New", "Bestseller"
                const badgeWords = ['popular', 'new', 'bestseller', 'sold out', 'trending'];
                for (const line of lines) {
                    if (line.length > 5 && !badgeWords.includes(line.toLowerCase()) && !line.match(/^\\d/) && !line.match(/^From/) && !line.match(/^Hosted/i)) {
                        title = line;
                        break;
                    }
                }
                if (!title) title = lines[0];
            }

            let hostName = '';
            let duration = '';
            let price = '';
            let rating = '';
            let numReviews = '';

            for (const line of lines) {
                if (line.match(/hosted\\s+by/i)) {
                    hostName = line.replace(/hosted\\s+by\\s*/i, '').trim();
                }
                if (line.match(/\\d+(\\.\\d+)?\\s*(hour|min|day)/i) && !duration) {
                    duration = line;
                }
                if (line.match(/\\$\\d+|From\\s*\\$/i) && !price) {
                    price = line;
                }
                if (line.match(/^[\\d.]+\\s*\\(/)) {
                    const m = line.match(/^([\\d.]+)\\s*\\(([\\d,]+)/);
                    if (m) { rating = m[1]; numReviews = m[2]; }
                }
                if (line.match(/^\\d+\\.\\d+$/) && !rating) {
                    rating = line;
                }
            }

            if (title.length > 3) {
                items.push({title, host_name: hostName, duration, price_per_person: price, rating, num_reviews: numReviews});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ExperienceItem()
        item.title = d.get("title", "")
        item.host_name = d.get("host_name", "")
        item.duration = d.get("duration", "")
        item.price_per_person = d.get("price_per_person", "")
        item.rating = d.get("rating", "")
        item.num_reviews = d.get("num_reviews", "")
        result.items.append(item)

    # ── Print results ─────────────────────────────────────────────────
    for i, item in enumerate(result.items, 1):
        print(f"\n  Experience {i}:")
        print(f"    Title:          {item.title}")
        print(f"    Host:           {item.host_name}")
        print(f"    Duration:       {item.duration}")
        print(f"    Price/Person:   {item.price_per_person}")
        print(f"    Rating:         {item.rating}")
        print(f"    Reviews:        {item.num_reviews}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("airbnb_experiences")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = ExperienceSearchRequest()
            result = airbnb_experience_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} experiences")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
