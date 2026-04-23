"""
Auto-generated Playwright script (Python)
justwatch.com – Streaming Availability Search
Movie: Inception

Generated on: 2026-04-18T01:22:08.465Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class JustWatchRequest:
    movie_title: str = "Inception"
    movie_slug: str = "inception"


@dataclass(frozen=True)
class StreamingOffer:
    service_name: str = ""
    availability_type: str = ""
    price: str = ""


@dataclass(frozen=True)
class JustWatchResult:
    offers: list = None  # list[StreamingOffer]


def justwatch_search(page: Page, request: JustWatchRequest) -> JustWatchResult:
    """Search JustWatch for streaming availability."""
    slug = request.movie_slug
    print(f"  Movie: {request.movie_title}\n")

    # ── Navigate to movie page ────────────────────────────────────────
    url = f"https://www.justwatch.com/us/movie/{slug}"
    print(f"Loading {url}...")
    checkpoint("Navigate to JustWatch movie page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Extract streaming offers ──────────────────────────────────────
    offers = page.evaluate(r"""() => {
        const containers = document.querySelectorAll('div.offer__content');
        const results = [];
        const seen = new Set();
        for (const c of containers) {
            const img = c.querySelector('img[alt]');
            if (!img || img.alt === 'JustWatch') continue;
            const service = img.alt;
            const text = c.innerText;
            let offerType = '';
            if (text.includes('Subscription')) offerType = 'Stream';
            else if (text.includes('Rent')) offerType = 'Rent';
            else if (text.includes('Buy')) offerType = 'Buy';
            else if (text.includes('Bundle')) offerType = 'Bundle';
            else continue;
            const priceMatch = text.match(/(\$[\d.]+(?:\s*\/\s*month)?)/);
            const price = priceMatch ? priceMatch[1] : '';
            const key = service + '|' + offerType + '|' + price;
            if (seen.has(key)) continue;
            seen.add(key);
            results.push({ service_name: service, availability_type: offerType, price });
        }
        return results;
    }""")

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f'JustWatch - "{request.movie_title}" Streaming Availability')
    print("=" * 60)
    for idx, o in enumerate(offers, 1):
        price_str = f" ({o['price']})" if o['price'] else ""
        print(f"  {idx}. {o['service_name']} [{o['availability_type']}]{price_str}")

    print(f"\nFound {len(offers)} offers")
    return JustWatchResult(
        offers=[StreamingOffer(**o) for o in offers]
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("justwatch_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = justwatch_search(page, JustWatchRequest())
            print(f"\nReturned {len(result.offers or [])} offers")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
