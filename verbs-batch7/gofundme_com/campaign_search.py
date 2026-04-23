"""
Auto-generated Playwright script (Python)
GoFundMe – Search campaigns

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, urllib.parse
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CampaignSearchRequest:
    search_query: str = "education"
    max_results: int = 5


@dataclass
class Campaign:
    title: str = ""
    organizer: str = ""
    raised: str = ""
    progress_pct: str = ""
    url: str = ""


@dataclass
class CampaignSearchResult:
    campaigns: List[Campaign] = field(default_factory=list)


def campaign_search(page: Page, request: CampaignSearchRequest) -> CampaignSearchResult:
    """Search GoFundMe campaigns and extract results."""
    print(f"  Query: {request.search_query}")
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Navigate to GoFundMe search")
    q = urllib.parse.quote_plus(request.search_query)
    page.goto(f"https://www.gofundme.com/s?q={q}", wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    checkpoint("Extract campaign results")
    result = CampaignSearchResult()

    items = page.evaluate(
        r"""(max) => {
            const cards = document.querySelectorAll('[class*="full-state-list-card_card"]');
            const results = [];
            for (let i = 0; i < cards.length && results.length < max; i++) {
                const card = cards[i];

                // Title
                const titleEl = card.querySelector('[class*="fundName"]');
                const title = titleEl ? titleEl.textContent.trim() : '';

                // Organizer
                const orgEl = card.querySelector('[class*="organizer"] span');
                const organizer = orgEl ? orgEl.textContent.trim() : '';

                // Amount raised
                const labelEl = card.querySelector('label[class*="goal-bar-label"]');
                const raised = labelEl ? labelEl.textContent.trim() : '';

                // Progress percentage
                const progressEl = card.querySelector('progress');
                const pct = progressEl ? progressEl.value + '%' : '';

                // URL
                const linkEl = card.querySelector('a[href]');
                const url = linkEl ? linkEl.href : '';

                if (title) {
                    results.push({title, organizer, raised, progress_pct: pct, url});
                }
            }
            return results;
        }""",
        request.max_results,
    )

    for item in items:
        c = Campaign()
        c.title = item.get("title", "")
        c.organizer = item.get("organizer", "")
        c.raised = item.get("raised", "")
        c.progress_pct = item.get("progress_pct", "")
        c.url = item.get("url", "")
        result.campaigns.append(c)

    for i, c in enumerate(result.campaigns):
        print(f"  Campaign {i + 1}:")
        print(f"    Title:        {c.title}")
        print(f"    Organizer:    {c.organizer}")
        print(f"    Raised:       {c.raised}")
        print(f"    Progress:     {c.progress_pct}")
        print(f"    URL:          {c.url}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("gofundme")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = CampaignSearchRequest()
            result = campaign_search(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.campaigns)} campaigns")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
