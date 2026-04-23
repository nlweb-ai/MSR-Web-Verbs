"""
Auto-generated Playwright script (Python)
ranker.com – Ranked Lists
Query: "best sci-fi movies"

Generated on: 2026-04-18T02:02:37.356Z
Recorded 3 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class RankerRequest:
    query: str = "best sci-fi movies"
    max_items: int = 10


@dataclass(frozen=True)
class RankedItem:
    rank: str = ""
    item_name: str = ""
    votes: str = ""


@dataclass(frozen=True)
class RankerResult:
    list_title: str = ""
    total_voters: str = ""
    items: list = None  # list[RankedItem]


def ranker_search(page: Page, request: RankerRequest) -> RankerResult:
    """Search Ranker for lists and extract top items."""
    print(f"  Query: {request.query}")
    print(f"  Max items: {request.max_items}\n")

    # ── Search ────────────────────────────────────────────────────────
    search_url = f"https://www.ranker.com/search?q={quote_plus(request.query)}"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to Ranker search")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Find and navigate to first list ───────────────────────────────
    first_list = page.evaluate(r"""() => {
        const links = document.querySelectorAll('a[href*="/list/"]');
        for (const link of links) {
            const href = link.href;
            if (href.includes('/list/') && !href.includes('/search')) {
                return href;
            }
        }
        return null;
    }""")

    if not first_list:
        print("No list found in search results")
        return RankerResult()

    print(f"Navigating to list: {first_list}")
    checkpoint("Navigate to list page")
    page.goto(first_list, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Extract list title and metadata ───────────────────────────────
    list_title = page.title().replace(" | Ranker", "").strip()

    voters = page.evaluate(r"""() => {
        const text = document.body.innerText;
        const match = text.match(/(\d[\d,.]*K?)\s*VOTERS/i);
        return match ? match[1] : '';
    }""")

    # ── Extract ranked items ──────────────────────────────────────────
    items = page.evaluate(r"""(maxItems) => {
        const listItems = document.querySelectorAll('[class*="listItem"]');
        const results = [];
        for (let i = 0; i < Math.min(listItems.length, maxItems); i++) {
            const li = listItems[i];
            const text = li.innerText;
            const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);

            // Rank: first line (number)
            const rank = lines[0] && lines[0].match(/^\d+$/) ? lines[0] : String(i + 1);

            // Item name: second line
            const itemName = lines.length > 1 ? lines[1] : '';

            // Votes: look for "NNN VOTES" pattern
            let votes = '';
            const voteMatch = text.match(/(\d[\d,]*)\s*VOTES/i);
            if (voteMatch) votes = voteMatch[1];

            results.push({ rank, item_name: itemName, votes });
        }
        return results;
    }""", request.max_items)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Ranker List: {list_title}")
    print(f"Total Voters: {voters}")
    print("=" * 60)
    for item in items:
        print(f"\n  #{item['rank']}. {item['item_name']}")
        print(f"      Votes: {item['votes']}")

    print(f"\nExtracted {len(items)} items")
    return RankerResult(
        list_title=list_title,
        total_voters=voters,
        items=[RankedItem(**item) for item in items],
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("ranker_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = ranker_search(page, RankerRequest())
            print(f"\nReturned {len(result.items or [])} items")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
