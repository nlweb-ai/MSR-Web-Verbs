import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MeetupSearchRequest:
    query: str = "hiking"
    location: str = "us--co--Denver"
    location_label: str = "Denver, CO"
    max_results: int = 5


@dataclass(frozen=True)
class MeetupGroup:
    name: str = ""
    members: str = ""
    rating: str = "N/A"
    location: str = "N/A"


@dataclass(frozen=True)
class MeetupSearchResult:
    groups: tuple = ()


MEMBERS_RE = re.compile(r'^([\d,]+)\s+members$')
RATING_RE = re.compile(r'^\d+\.\d$')


# Search for meetup groups on meetup.com by keyword and location.
# Extracts group name, member count, rating, and location for up to max_results groups.
def meetup_search(page: Page, request: MeetupSearchRequest) -> MeetupSearchResult:
    from urllib.parse import quote_plus

    print(f"  Query: {request.query}")
    print(f"  Location: {request.location_label}\n")

    url = f"https://www.meetup.com/find/?keywords={quote_plus(request.query)}&location={request.location}&source=GROUPS&eventType=group"
    print(f"Loading {url}...")
    checkpoint("Navigate to page")
    page.goto(url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(10000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    results = []

    # Parse group listings
    # Pattern: location -> optional rating -> group name -> description -> 'N members'
    i = 0
    # Skip to after the category filters (after 'Movements & Politics')
    while i < len(text_lines):
        if text_lines[i] == "Movements & Politics":
            i += 1
            break
        i += 1

    # Now parse groups
    while i < len(text_lines) and len(results) < request.max_results:
        line = text_lines[i]

        # Look for members line
        m = MEMBERS_RE.match(line)
        if m:
            members = m.group(1)
            name = None
            rating = None
            loc = None

            # Line before members is description
            if i >= 2:
                j = i - 2
                name = text_lines[j]

                # Look further back for rating and location
                for k in range(j - 1, max(j - 5, 0), -1):
                    kline = text_lines[k]
                    if RATING_RE.match(kline):
                        rating = kline
                    elif re.match(r'^[A-Z][a-z]+.*,\s*[A-Z]{2}$', kline):
                        loc = kline
                        break

            if name and name not in ('New group', 'Report Ad'):
                results.append(MeetupGroup(
                    name=name,
                    members=members,
                    rating=rating or "N/A",
                    location=loc or "N/A",
                ))
        i += 1

    print("=" * 60)
    print(f"Meetup Groups: {request.query} near {request.location_label}")
    print("=" * 60)
    for idx, g in enumerate(results, 1):
        print(f"\n{idx}. {g.name}")
        print(f"   Members:  {g.members}")
        print(f"   Rating:   {g.rating}")
        print(f"   Location: {g.location}")

    print(f"\nFound {len(results)} groups")

    return MeetupSearchResult(groups=tuple(results))


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_user_data = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            chrome_user_data,
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        req = MeetupSearchRequest()
        result = meetup_search(page, req)
        print(f"\nReturned {len(result.groups)} groups")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)