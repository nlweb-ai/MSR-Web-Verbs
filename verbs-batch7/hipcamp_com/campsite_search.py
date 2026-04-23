"""
Auto-generated Playwright script (Python)
Hipcamp – Search camping sites

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re, urllib.parse
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CampsiteSearchRequest:
    location: str = "Joshua Tree, CA"
    lat: str = "34.1347"
    lng: str = "-116.3131"
    max_results: int = 5


@dataclass
class Campsite:
    name: str = ""
    price: str = ""
    site_type: str = ""
    rating: str = ""
    reviews: str = ""
    location: str = ""


@dataclass
class CampsiteSearchResult:
    campsites: List[Campsite] = field(default_factory=list)


def campsite_search(page: Page, request: CampsiteSearchRequest) -> CampsiteSearchResult:
    """Search Hipcamp for camping sites and extract listings."""
    print(f"  Location: {request.location}")
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Navigate to Hipcamp search")
    q = urllib.parse.quote_plus(request.location)
    page.goto(
        f"https://www.hipcamp.com/en-US/search?q={q}&lat={request.lat}&lng={request.lng}",
        wait_until="domcontentloaded",
    )
    page.wait_for_timeout(8000)

    checkpoint("Extract campsite listings")
    result = CampsiteSearchResult()

    items = page.evaluate(
        r"""(max) => {
            const links = document.querySelectorAll('a[href*="/land/"]');
            const seen = new Set();
            const results = [];
            for (const a of links) {
                if (results.length >= max) break;
                const href = a.href;
                if (seen.has(href)) continue;
                seen.add(href);

                const text = a.textContent.trim();
                // Parse: "95%(905)The Castle House: Estate10 sites · Tents, RVs, LodgingJoshua Tree, CA · 15 minfrom$66 / night"
                // Or: "NewBooked 1 timeRhythms Of Nature...from$40 / night"

                // Rating + reviews
                const ratingMatch = text.match(/^(\d+)%\((\d+)\)/);
                let rating = '', reviews = '';
                let rest = text;
                if (ratingMatch) {
                    rating = ratingMatch[1] + '%';
                    reviews = ratingMatch[2];
                    rest = text.slice(ratingMatch[0].length);
                } else if (text.startsWith('New')) {
                    rest = text.replace(/^New(Booked \d+ times?)?/, '');
                }

                // Price
                const priceMatch = rest.match(/from\$(\d+)\s*\/\s*night/);
                const price = priceMatch ? '$' + priceMatch[1] + '/night' : '';

                // Site type + location
                // Pattern: "10 sites · Tents, RVs, LodgingJoshua Tree, CA · 15 min"
                const siteInfoMatch = rest.match(/\d+\s*sites?\s*·\s*((?:Tents|RVs|Lodging)(?:,\s*(?:Tents|RVs|Lodging))*)/);
                const siteType = siteInfoMatch ? siteInfoMatch[1].trim() : '';

                // Location after site type: "CityName, ST"
                const afterType = siteInfoMatch ? rest.slice(rest.indexOf(siteInfoMatch[0]) + siteInfoMatch[0].length) : rest;
                const locMatch = afterType.match(/^([A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s*[A-Z]{2})/);
                const loc = locMatch ? locMatch[1] : '';

                // Name: between rating/reviews and "N sites"
                let name = '';
                const siteCountMatch = rest.match(/(\d+\s*sites?\s*·)/);
                if (siteCountMatch) {
                    name = rest.slice(0, siteCountMatch.index).trim();
                } else {
                    name = rest.slice(0, 50).trim();
                }

                const url = href.split('?')[0];

                if (name) {
                    results.push({name, price, site_type: siteType, rating, reviews, location: loc, url});
                }
            }
            return results;
        }""",
        request.max_results,
    )

    for item in items:
        c = Campsite()
        c.name = item.get("name", "")
        c.price = item.get("price", "")
        c.site_type = item.get("site_type", "")
        c.rating = item.get("rating", "")
        c.reviews = item.get("reviews", "")
        c.location = item.get("location", "")
        result.campsites.append(c)

    for i, c in enumerate(result.campsites):
        print(f"  Campsite {i + 1}:")
        print(f"    Name:      {c.name}")
        print(f"    Price:     {c.price}")
        print(f"    Type:      {c.site_type}")
        print(f"    Rating:    {c.rating}")
        print(f"    Reviews:   {c.reviews}")
        print(f"    Location:  {c.location}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("hipcamp")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = CampsiteSearchRequest()
            result = campsite_search(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.campsites)} campsites")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
