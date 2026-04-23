"""
Auto-generated Playwright script (Python)
news.ycombinator.com – Top Stories
Extract top 10 stories from Hacker News

Generated on: 2026-04-18T01:42:20.702Z
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
class HackerNewsRequest:
    max_results: int = 10


@dataclass(frozen=True)
class HNStory:
    title: str = ""
    url: str = ""
    points: str = ""
    author: str = ""
    num_comments: str = ""
    time_posted: str = ""


@dataclass(frozen=True)
class HackerNewsResult:
    stories: list = None  # list[HNStory]


def hackernews_top(page: Page, request: HackerNewsRequest) -> HackerNewsResult:
    """Extract top stories from Hacker News."""
    print(f"  Max results: {request.max_results}\n")

    # ── Navigate to front page ────────────────────────────────────────
    url = "https://news.ycombinator.com"
    print(f"Loading {url}...")
    checkpoint("Navigate to Hacker News")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # ── Extract stories ───────────────────────────────────────────────
    stories = page.evaluate(r"""(maxResults) => {
        const rows = document.querySelectorAll('tr.athing');
        const results = [];
        for (let i = 0; i < Math.min(rows.length, maxResults); i++) {
            const row = rows[i];
            const titleEl = row.querySelector('.titleline a');
            const domainEl = row.querySelector('.sitebit .sitestr');
            const subtextRow = row.nextElementSibling;
            const scoreEl = subtextRow ? subtextRow.querySelector('.score') : null;
            const userEl = subtextRow ? subtextRow.querySelector('.hnuser') : null;
            const ageEl = subtextRow ? subtextRow.querySelector('.age') : null;
            const commentLinks = subtextRow ? [...subtextRow.querySelectorAll('a')] : [];
            const commentEl = commentLinks.find(a => a.innerText.includes('comment'));

            const title = titleEl ? titleEl.innerText : '';
            const storyUrl = titleEl ? titleEl.href : '';
            const domain = domainEl ? ' (' + domainEl.innerText + ')' : '';
            const points = scoreEl ? scoreEl.innerText : '';
            const author = userEl ? userEl.innerText : '';
            const age = ageEl ? ageEl.innerText : '';
            const comments = commentEl ? commentEl.innerText : '0 comments';

            results.push({
                title,
                url: storyUrl + domain,
                points,
                author,
                num_comments: comments,
                time_posted: age,
            });
        }
        return results;
    }""", request.max_results)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("Hacker News - Top Stories")
    print("=" * 60)
    for idx, s in enumerate(stories, 1):
        print(f"\n  {idx}. {s['title']}")
        print(f"     URL: {s['url']}")
        print(f"     {s['points']} | by {s['author']} | {s['time_posted']} | {s['num_comments']}")

    print(f"\nFound {len(stories)} stories")
    return HackerNewsResult(
        stories=[HNStory(**s) for s in stories]
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("news_ycombinator_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = hackernews_top(page, HackerNewsRequest())
            print(f"\nReturned {len(result.stories or [])} stories")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
