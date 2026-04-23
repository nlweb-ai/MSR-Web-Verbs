import re
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


PRICE_RE = re.compile(r'^\$[\d,]+(?: \u2013 \$[\d,]+)?$')
SITES_RE = re.compile(r'^(\d+) Accessible Campsite')


@dataclass(frozen=True)
class RecreationSearchRequest:
    query: str = "Yellowstone"
    max_results: int = 5


@dataclass(frozen=True)
class Campground:
    name: str = ""
    location: str = ""
    sites: str = ""
    fee: str = ""


@dataclass(frozen=True)
class RecreationSearchResult:
    campgrounds: list = None  # list[Campground]


# Search recreation.gov for campgrounds matching a query and extract listing details
# including name, location, number of sites, and nightly fee.
def recreation_search(page: Page, request: RecreationSearchRequest) -> RecreationSearchResult:
    query = request.query
    max_results = request.max_results
    print(f"  Query: {query}\n")

    url = f"https://www.recreation.gov/search?q={quote_plus(query)}&entity_type=campground"
    print(f"Loading {url}...")
    checkpoint("Navigate to page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    results = []
    i = 0
    while i < len(text_lines) and len(results) < max_results:
        if text_lines[i] == 'CAMPING':
            name = text_lines[i + 1] if i + 1 < len(text_lines) else 'Unknown'

            location = 'N/A'
            fee = 'N/A'
            sites = 'N/A'
            for j in range(i + 2, min(i + 15, len(text_lines))):
                if text_lines[j].startswith('Near '):
                    location = text_lines[j].replace('Near ', '')
                sm = SITES_RE.match(text_lines[j])
                if sm:
                    sites = sm.group(1)
                if PRICE_RE.match(text_lines[j]):
                    fee = text_lines[j] + ' / night'
                    break

            results.append(Campground(
                name=name,
                location=location,
                sites=sites,
                fee=fee,
            ))

        i += 1

    print("=" * 60)
    print(f"Campgrounds near {query}")
    print("=" * 60)
    for idx, r in enumerate(results, 1):
        print(f"\n{idx}. {r.name}")
        print(f"   Location: {r.location}")
        print(f"   Sites:    {r.sites}")
        print(f"   Fee:      {r.fee}")

    print(f"\nFound {len(results)} campgrounds")

    return RecreationSearchResult(campgrounds=results)


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    profile_path = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default",
    )
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            profile_path,
            headless=False,
            channel="chrome",
        )
        page = context.pages[0] if context.pages else context.new_page()
        result = recreation_search(page, RecreationSearchRequest())
        print(f"\nReturned {len(result.campgrounds)} campgrounds")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)