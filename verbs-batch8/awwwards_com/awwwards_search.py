"""
Auto-generated Playwright script (Python)
Awwwards – Browse Award-Winning Websites

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class AwwwardsRequest:
    max_results: int = 5


@dataclass
class AwardedSite:
    site_name: str = ""
    agency: str = ""
    country: str = ""
    award_type: str = ""
    score: str = ""
    site_url: str = ""


@dataclass
class AwwwardsResult:
    sites: list = field(default_factory=list)


def awwwards_search(page: Page, request: AwwwardsRequest) -> AwwwardsResult:
    """Browse awwwards.com for award-winning websites."""
    print(f"  Fetching top {request.max_results} award-winning sites...\n")

    # ── Navigate ──────────────────────────────────────────────────────
    url = "https://www.awwwards.com/websites/"
    print(f"Loading {url}...")
    checkpoint("Navigate to Awwwards websites")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Extract sites ─────────────────────────────────────────────────
    raw_sites = page.evaluate(r"""(maxResults) => {
        const cards = document.querySelectorAll('li[class*="js-collectable"], div[class*="box-item"], article[class*="js-collectable"]');
        const results = [];
        for (let i = 0; i < Math.min(cards.length, maxResults); i++) {
            const card = cards[i];
            const titleEl = card.querySelector('h2, h3, [class*="title"], a[class*="title"]');
            const agencyEl = card.querySelector('[class*="by"] a, [class*="agency"], [class*="author"]');
            const countryEl = card.querySelector('[class*="country"], [class*="location"]');
            const awardEl = card.querySelector('[class*="award"], [class*="badge"], [class*="label"]');
            const scoreEl = card.querySelector('[class*="score"], [class*="vote"], [class*="rating"]');
            const linkEl = card.querySelector('a[href*="sites/"]');

            results.push({
                site_name: titleEl ? titleEl.innerText.trim() : '',
                agency: agencyEl ? agencyEl.innerText.trim() : '',
                country: countryEl ? countryEl.innerText.trim() : '',
                award_type: awardEl ? awardEl.innerText.trim() : '',
                score: scoreEl ? scoreEl.innerText.trim() : '',
                site_url: linkEl ? linkEl.href : '',
            });
        }
        return results;
    }""", request.max_results)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("Awwwards: Award-Winning Websites")
    print("=" * 60)
    for idx, s in enumerate(raw_sites, 1):
        print(f"\n  {idx}. {s['site_name']}")
        print(f"     Agency: {s['agency']}")
        if s['country']:
            print(f"     Country: {s['country']}")
        if s['award_type']:
            print(f"     Award: {s['award_type']}")
        print(f"     Score: {s['score']}")
        if s['site_url']:
            print(f"     URL: {s['site_url']}")

    sites = [AwardedSite(**s) for s in raw_sites]
    return AwwwardsResult(sites=sites)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("awwwards_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = awwwards_search(page, AwwwardsRequest())
            print(f"\nReturned {len(result.sites)} sites")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
