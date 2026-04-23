"""
Auto-generated Playwright script (Python)
Charity Navigator – Charity Search
Query: "disaster relief"

Generated on: 2026-04-18T05:03:20.307Z
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
class CharityRequest:
    query: str = "disaster relief"
    max_charities: int = 5


@dataclass
class Charity:
    name: str = ""
    rating: str = ""
    financial_score: str = ""
    accountability_score: str = ""
    url: str = ""


@dataclass
class CharityResult:
    charities: list = field(default_factory=list)


def charitynavigator_search(page: Page, request: CharityRequest) -> CharityResult:
    """Search Charity Navigator for charities by keyword."""
    print(f"  Query: {request.query}\n")

    # ── Step 1: Search Charity Navigator ──────────────────────────────
    url = f"https://www.charitynavigator.org/search?q={quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Search Charity Navigator")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    # ── Step 2: Extract charity results ───────────────────────────────
    checkpoint("Extract charity data")
    charities_data = page.evaluate(r"""(maxResults) => {
        const cards = document.querySelectorAll('[class*="SearchResult"][aria-label="nonprofit profile page"]');
        const results = [];
        for (const card of cards) {
            if (results.length >= maxResults) break;

            // Name from h2
            const h2 = card.querySelector('h2');
            const name = h2 ? h2.innerText.trim() : '';
            if (!name) continue;

            // Rating text (e.g. "FOUR-STAR CHARITY")
            const text = card.innerText;
            let rating = '';
            const starMatch = text.match(/(ONE|TWO|THREE|FOUR)-STAR CHARITY/i);
            if (starMatch) {
                const map = { 'ONE': '1', 'TWO': '2', 'THREE': '3', 'FOUR': '4' };
                rating = (map[starMatch[1].toUpperCase()] || '') + '/4 stars';
            }

            // Score percentage
            let score = '';
            const pctMatch = text.match(/(\d{1,3})%/);
            if (pctMatch) score = pctMatch[1] + '%';

            // Location
            let location = '';
            const locDiv = card.querySelector('h2 + div');
            if (locDiv) {
                const locText = locDiv.innerText.trim().split('|')[0].trim();
                if (locText) location = locText;
            }

            // Link (EIN link)
            const link = card.querySelector('a[href*="/ein/"]');
            const charityUrl = link ? link.href : '';

            // Cause/category
            let cause = '';
            const tags = card.querySelectorAll('a[class*="SearchResultTag"]');
            for (const tag of tags) {
                const t = tag.innerText.trim();
                if (!t.includes('revenue') && !t.includes('annual')) {
                    cause = t;
                    break;
                }
            }

            results.push({
                name, rating, score, location, cause, url: charityUrl
            });
        }
        return results;
    }""", request.max_charities)

    result = CharityResult(
        charities=[Charity(
            name=c['name'],
            rating=c['rating'],
            financial_score=c['score'],
            accountability_score='',
        ) for c in charities_data]
    )

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Charity Navigator: {request.query}")
    print("=" * 60)
    for i, c in enumerate(charities_data, 1):
        print(f"\n  {i}. {c['name']}")
        print(f"     Rating: {c['rating']}")
        print(f"     Score:  {c['score']}")
        if c.get('location'):
            print(f"     Location: {c['location']}")
        if c.get('cause'):
            print(f"     Cause: {c['cause']}")
        if c.get('url'):
            print(f"     URL: {c['url']}")
    print(f"\n  Total: {len(result.charities)} charities")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("charitynavigator_org")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = charitynavigator_search(page, CharityRequest())
            print(f"\nReturned {len(result.charities)} charities")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
