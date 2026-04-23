"""
Auto-generated Playwright script (Python)
Kickstarter – Search projects

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
class ProjectSearchRequest:
    query: str = "board game"
    max_results: int = 5


@dataclass
class Project:
    name: str = ""
    creator: str = ""
    days_left: str = ""
    percent_funded: str = ""
    description: str = ""
    category: str = ""


@dataclass
class ProjectSearchResult:
    projects: List[Project] = field(default_factory=list)


def project_search(page: Page, request: ProjectSearchRequest) -> ProjectSearchResult:
    """Search Kickstarter for projects and extract listing info."""
    print(f"  Query: {request.query}")
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Navigate to Kickstarter search")
    q = urllib.parse.quote_plus(request.query)
    page.goto(
        f"https://www.kickstarter.com/discover/advanced?term={q}&sort=magic",
        wait_until="domcontentloaded",
    )
    page.wait_for_timeout(6000)

    checkpoint("Extract project listings")
    result = ProjectSearchResult()

    items = page.evaluate(
        r"""(max) => {
            // Search results are in the second .js-project-group (group index 1)
            const groups = document.querySelectorAll('.js-project-group');
            const searchGroup = groups.length > 1 ? groups[1] : groups[0];
            if (!searchGroup) return [];

            const cards = searchGroup.querySelectorAll('.js-react-proj-card');
            const results = [];
            for (let i = 0; i < cards.length && results.length < max; i++) {
                const card = cards[i];
                const titleEl = card.querySelector('.project-card__title');
                const name = titleEl ? titleEl.textContent.trim() : '';
                if (!name) continue;

                const lines = card.innerText.split('\n').map(l => l.trim()).filter(Boolean);

                // Creator: line after title
                let creator = '';
                let daysLeft = '';
                let percentFunded = '';
                let description = '';
                let category = '';

                const titleIdx = lines.indexOf(name);
                if (titleIdx >= 0 && titleIdx + 1 < lines.length) {
                    creator = lines[titleIdx + 1];
                }

                // Find "X days left • Y% funded" line
                for (const line of lines) {
                    const fundMatch = line.match(/(\d+)\s*days?\s*left\s*•\s*(\d+)%\s*funded/);
                    if (fundMatch) {
                        daysLeft = fundMatch[1];
                        percentFunded = fundMatch[2] + '%';
                    }
                }

                // Description and category come after the funding line
                for (let j = 0; j < lines.length; j++) {
                    if (lines[j].match(/days?\s*left\s*•/)) {
                        // Lines after funding: description then category
                        const remaining = lines.slice(j + 1);
                        if (remaining.length >= 2) {
                            description = remaining.slice(0, -1).join(' ');
                            category = remaining[remaining.length - 1];
                        } else if (remaining.length === 1) {
                            category = remaining[0];
                        }
                        break;
                    }
                }

                results.push({name, creator, days_left: daysLeft, percent_funded: percentFunded, description, category});
            }
            return results;
        }""",
        request.max_results,
    )

    for item in items:
        p = Project()
        p.name = item.get("name", "")
        p.creator = item.get("creator", "")
        p.days_left = item.get("days_left", "")
        p.percent_funded = item.get("percent_funded", "")
        p.description = item.get("description", "")
        p.category = item.get("category", "")
        result.projects.append(p)

    for i, p in enumerate(result.projects):
        print(f"  Project {i + 1}:")
        print(f"    Name:         {p.name}")
        print(f"    Creator:      {p.creator}")
        print(f"    Days Left:    {p.days_left}")
        print(f"    Funded:       {p.percent_funded}")
        print(f"    Description:  {p.description}")
        print(f"    Category:     {p.category}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("kickstarter")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = ProjectSearchRequest()
            result = project_search(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.projects)} projects")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
