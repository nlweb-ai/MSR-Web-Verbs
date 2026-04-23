import re
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


# Grant entry markers
DATE_RE = re.compile(r'^(?:TBD|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4})$')
STATUS_VALS = {'Open', 'Forecasted', 'Closed', 'Archived'}


@dataclass(frozen=True)
class GrantsSearchRequest:
    query: str = "STEM education"
    max_results: int = 5


@dataclass(frozen=True)
class GrantItem:
    title: str
    agency: str
    funding: str
    close_date: str


@dataclass(frozen=True)
class GrantsSearchResult:
    grants: list  # list[GrantItem]


# Search Grants.gov for grants matching a query.
# Navigates to the Grants.gov search page, waits for results to load,
# parses grant entries from the page text, and returns up to max_results
# grants with title, agency, funding amount, and close date.
def grants_search(page: Page, request: GrantsSearchRequest) -> GrantsSearchResult:
    print(f"  Query: {request.query}")
    print(f"  Max results: {request.max_results}\n")

    results = []

    url = f"https://simpler.grants.gov/search?query={quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to page")
    page.goto(url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Parse grant entries from text
    # Pattern: close_date, status, title, number, agency, posted_date, expected_awards, award_min, award_max
    i = 0
    while i < len(text_lines) and len(results) < request.max_results:
        line = text_lines[i]
        # Look for a date line followed by a status
        if DATE_RE.match(line) and i + 1 < len(text_lines) and text_lines[i + 1] in STATUS_VALS:
            close_date = line
            status = text_lines[i + 1]
            title = text_lines[i + 2] if i + 2 < len(text_lines) else ""
            agency = ""
            award_min = ""
            award_max = ""
            # Look ahead for agency and funding
            for j in range(i + 3, min(i + 10, len(text_lines))):
                jline = text_lines[j]
                if jline.startswith("Number:"):
                    continue
                if jline.startswith("Posted date:"):
                    continue
                if jline.startswith("Expected awards:"):
                    continue
                if jline.startswith("$"):
                    if not award_min:
                        award_min = jline
                    else:
                        award_max = jline
                        break
                elif not agency and not jline.startswith("$") and DATE_RE.match(jline) is None and jline not in STATUS_VALS:
                    agency = jline

            funding = award_min + " - " + award_max if award_min and award_max else award_min or "N/A"
            results.append(GrantItem(
                title=title,
                agency=agency,
                funding=funding,
                close_date=close_date,
            ))
            i += 8  # skip past this entry
        else:
            i += 1

    print("=" * 70)
    print(f"Grants.gov Search: {request.query}")
    print("=" * 70)
    for idx, r in enumerate(results, 1):
        print(f"\n{idx}. {r.title}")
        print(f"   Agency:     {r.agency}")
        print(f"   Funding:    {r.funding}")
        print(f"   Close Date: {r.close_date}")

    print(f"\nFound {len(results)} grants")

    return GrantsSearchResult(grants=results)


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_profile = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default",
    )
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            chrome_profile,
            headless=False,
            channel="chrome",
        )
        page = context.pages[0] if context.pages else context.new_page()
        request = GrantsSearchRequest()
        result = grants_search(page, request)
        print(f"\nReturned {len(result.grants)} grants")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)