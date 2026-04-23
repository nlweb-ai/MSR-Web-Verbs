"""
Auto-generated Playwright script (Python)
nomadlist.com – Top Cities for Digital Nomads
Extract top 10 cities

Generated on: 2026-04-18T01:46:22.368Z
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
class NomadListRequest:
    max_results: int = 10


@dataclass(frozen=True)
class NomadCity:
    city_name: str = ""
    country: str = ""
    overall_score: str = ""
    internet_speed: str = ""
    cost_per_month: str = ""
    temperature: str = ""


@dataclass(frozen=True)
class NomadListResult:
    cities: list = None  # list[NomadCity]


def nomadlist_top(page: Page, request: NomadListRequest) -> NomadListResult:
    """Extract top cities from NomadList."""
    print(f"  Max results: {request.max_results}\n")

    # ── Navigate to front page ────────────────────────────────────────
    url = "https://nomadlist.com"
    print(f"Loading {url}...")
    checkpoint("Navigate to NomadList")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Extract cities ────────────────────────────────────────────────
    cities = page.evaluate(r"""(maxResults) => {
        const lis = document.querySelectorAll('li[data-type="city"]');
        const results = [];
        for (let i = 0; i < Math.min(lis.length, maxResults); i++) {
            const li = lis[i];

            // City name from h2.itemName
            const nameEl = li.querySelector('h2.itemName');
            const cityName = nameEl ? nameEl.innerText.trim() : '';

            // Country from h3 or span after city name
            const countryEl = li.querySelector('h3') || li.querySelector('.itemSub');
            let country = '';
            if (countryEl) {
                country = countryEl.innerText.trim();
            } else {
                // Parse from text: line after city name
                const text = li.innerText;
                const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
                const nameIdx = lines.indexOf(cityName);
                if (nameIdx >= 0 && nameIdx + 1 < lines.length) {
                    country = lines[nameIdx + 1];
                }
            }

            // Overall score from rating class (r1-r5)
            const ratingEl = li.querySelector('span.rating-main-score');
            let overallScore = '';
            if (ratingEl) {
                const cls = ratingEl.className;
                const match = cls.match(/\br(\d)\b/);
                if (match) overallScore = match[1] + '/5';
            }

            // Cost from text
            const text = li.innerText;
            const costMatch = text.match(/(\$[\d,]+)\s*\/\s*mo/);
            const cost = costMatch ? costMatch[1] + '/mo' : '';

            // Internet speed from text
            const netMatch = text.match(/(\d+)\s*Mbps/);
            const internet = netMatch ? netMatch[1] + ' Mbps' : '';

            // Temperature from span.value.unit.metric (first one is feels-like)
            const tempEls = li.querySelectorAll('span.unit.metric');
            let temp = '';
            if (tempEls.length > 1) {
                temp = tempEls[1].innerText.trim();
            } else if (tempEls.length === 1) {
                temp = tempEls[0].innerText.trim();
            }

            results.push({
                city_name: cityName,
                country,
                overall_score: overallScore,
                internet_speed: internet,
                cost_per_month: cost,
                temperature: temp,
            });
        }
        return results;
    }""", request.max_results)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("NomadList - Top Cities for Digital Nomads")
    print("=" * 60)
    for idx, c in enumerate(cities, 1):
        print(f"\n  {idx}. {c['city_name']}, {c['country']}")
        print(f"     Overall: {c['overall_score']} | Cost: {c['cost_per_month']} | Internet: {c['internet_speed']}")
        if c['temperature']:
            print(f"     Temperature: {c['temperature']}")

    print(f"\nFound {len(cities)} cities")
    return NomadListResult(
        cities=[NomadCity(**c) for c in cities]
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("nomadlist_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = nomadlist_top(page, NomadListRequest())
            print(f"\nReturned {len(result.cities or [])} cities")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
