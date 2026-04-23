"""
Auto-generated Playwright script (Python)
ifixit.com – Repair Guide Search
Query: iPhone 15 battery replacement

Generated on: 2026-04-18T01:10:14.327Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil, urllib.parse
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class IFixitSearchRequest:
    search_query: str = "iPhone 15 battery replacement"
    max_results: int = 3


@dataclass(frozen=True)
class IFixitGuide:
    guide_title: str = ""
    difficulty: str = ""
    estimated_time: str = ""
    num_steps: int = 0
    guide_url: str = ""


@dataclass(frozen=True)
class IFixitSearchResult:
    guides: list = None  # list[IFixitGuide]


def ifixit_search(page: Page, request: IFixitSearchRequest) -> IFixitSearchResult:
    """Search iFixit for repair guides."""
    query = request.search_query
    max_results = request.max_results
    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    # ── Search page ───────────────────────────────────────────────────
    url = f"https://www.ifixit.com/Search?query={urllib.parse.quote_plus(query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to iFixit search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Get guide links ───────────────────────────────────────────────
    guide_links = page.evaluate(r"""(maxResults) => {
        const links = document.querySelectorAll('a[href*="/Guide/"]');
        const seen = new Set();
        const results = [];
        for (const a of links) {
            if (results.length >= maxResults) break;
            const href = a.href;
            if (seen.has(href)) continue;
            seen.add(href);
            const title = a.innerText.split('\n')[0].trim();
            if (title && title.length > 5) {
                results.push({ title, url: href });
            }
        }
        return results;
    }""", max_results)

    print(f"  Found {len(guide_links)} guide links")

    # ── Visit each guide page ─────────────────────────────────────────
    guides = []
    for g in guide_links:
        print(f"\n  Visiting: {g['url']}...")
        checkpoint(f"Visit guide: {g['title']}")
        page.goto(g["url"], wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        meta = page.evaluate(r"""() => {
            const text = document.body.innerText;
            const diffMatch = text.match(/(Very easy|Easy|Moderate|Difficult|Very difficult)/i);
            const timeMatch = text.match(/(\d+\s*[-\u2013]\s*\d+\s*(?:minutes|hours?)|\d+\s*(?:minutes|hours?))/i);
            const stepMatches = text.match(/Step \d+/g);
            const lastStep = stepMatches ? stepMatches[stepMatches.length - 1] : null;
            const numSteps = lastStep ? parseInt(lastStep.replace('Step ', '')) : 0;
            return {
                difficulty: diffMatch ? diffMatch[1] : 'N/A',
                time: timeMatch ? timeMatch[0] : 'N/A',
                numSteps
            };
        }""")

        guides.append(IFixitGuide(
            guide_title=g.get("title", ""),
            difficulty=meta.get("difficulty", "N/A"),
            estimated_time=meta.get("time", "N/A"),
            num_steps=meta.get("numSteps", 0),
            guide_url=g.get("url", ""),
        ))

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f'iFixit - "{query}" Repair Guides')
    print("=" * 60)
    for idx, g in enumerate(guides, 1):
        print(f"\n{idx}. {g.guide_title}")
        print(f"   Difficulty: {g.difficulty} | Time: {g.estimated_time} | Steps: {g.num_steps}")
        print(f"   URL: {g.guide_url}")

    print(f"\nFound {len(guides)} guides")
    return IFixitSearchResult(guides=guides)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("ifixit_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = ifixit_search(page, IFixitSearchRequest())
            print(f"\nReturned {len(result.guides or [])} guides")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
