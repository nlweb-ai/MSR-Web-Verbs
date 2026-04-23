"""
Playwright script (Python) — Lemmy Community Browser
Browse top communities on Lemmy and extract details.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class LemmyRequest:
    max_results: int = 5


@dataclass
class CommunityItem:
    name: str = ""
    subscribers: str = ""
    posts: str = ""
    comments: str = ""


@dataclass
class LemmyResult:
    items: List[CommunityItem] = field(default_factory=list)


# Browses the top communities on Lemmy and returns
# up to max_results communities with name, description, subscriber count, and post count.
def browse_lemmy_communities(page: Page, request: LemmyRequest) -> LemmyResult:
    url = "https://lemmy.ml/communities?listingType=Local&sort=TopMonth"
    print(f"Loading {url}...")
    checkpoint("Navigate to Lemmy communities page")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = LemmyResult()

    checkpoint("Extract community listings")
    js_code = """(max) => {
        const results = [];
        const rows = document.querySelectorAll('table tbody tr');
        for (const row of rows) {
            if (results.length >= max) break;
            const tds = row.querySelectorAll('td');
            if (tds.length < 5) continue;
            const nameEl = tds[0].querySelector('a');
            const name = nameEl ? nameEl.textContent.trim() : tds[0].textContent.trim();
            if (!name) continue;
            const posts = tds[1].textContent.trim();
            const comments = tds[2].textContent.trim();
            const subscribers = tds[4].textContent.trim();
            results.push({ name, subscribers, posts, comments });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = CommunityItem()
        item.name = d.get("name", "")
        item.subscribers = d.get("subscribers", "")
        item.posts = d.get("posts", "")
        item.comments = d.get("comments", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} communities:")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name}")
        print(f"     Subscribers: {item.subscribers}  Posts: {item.posts}  Comments: {item.comments}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("lemmy")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = browse_lemmy_communities(page, LemmyRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} communities")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
