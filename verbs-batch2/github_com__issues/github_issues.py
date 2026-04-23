"""
Playwright script (Python) — GitHub Repository Issues
Navigate to a repo's issues page and extract open issues with title, labels, and date.

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GithubIssuesRequest:
    repo: str
    max_results: int


@dataclass(frozen=True)
class GithubIssue:
    title: str
    labels: str
    created: str


@dataclass(frozen=True)
class GithubIssuesResult:
    repo: str
    issues: list[GithubIssue]


# Navigates to a GitHub repository's issues page and extracts
# up to max_results open issues with title, labels, and creation date.
def search_github_issues(
    page: Page,
    request: GithubIssuesRequest,
) -> GithubIssuesResult:
    repo = request.repo
    max_results = request.max_results

    print(f"  Repo: {repo}")
    print(f"  Max results: {max_results}\n")

    results: list[GithubIssue] = []

    try:
        print(f"Loading GitHub issues for {repo}...")
        checkpoint(f"Navigate to https://github.com/{repo}/issues")
        page.goto(f"https://github.com/{repo}/issues")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        print(f"STEP 1: Extract up to {max_results} open issues...")

        issue_links = page.locator('a[data-hovercard-type="issue"]')
        count = issue_links.count()
        print(f"  Found {count} issues")

        for i in range(min(count, max_results)):
            link = issue_links.nth(i)
            try:
                title = link.inner_text(timeout=2000).strip()
                if not title:
                    continue
                labels = "N/A"
                created = "N/A"
                try:
                    row = link.locator("xpath=ancestor::div[contains(@class, 'Row')]").first
                    time_el = row.locator("relative-time, time").first
                    created = time_el.get_attribute("datetime") or time_el.inner_text(timeout=2000).strip()
                except Exception:
                    pass
                try:
                    row = link.locator("xpath=ancestor::div[contains(@class, 'Row')]").first
                    label_els = row.locator('a[class*="label"], span[class*="Label"], [data-name]')
                    lbl_count = label_els.count()
                    if lbl_count > 0:
                        labels = ", ".join([label_els.nth(j).inner_text(timeout=1000).strip() for j in range(lbl_count)])
                except Exception:
                    pass

                results.append(GithubIssue(title=title, labels=labels, created=created))
                print(f"  {len(results)}. {title} | Labels: {labels} | Created: {created}")
            except Exception as e:
                print(f"  Error on row {i}: {e}")
                continue

        print(f"\nFound {len(results)} open issues for '{repo}':")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.title}")
            print(f"     Labels: {r.labels}  Created: {r.created}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return GithubIssuesResult(repo=repo, issues=results)


def test_search_github_issues() -> None:
    request = GithubIssuesRequest(repo="facebook/react", max_results=5)
    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir, channel="chrome", headless=False, viewport=None,
            args=["--disable-blink-features=AutomationControlled", "--disable-infobars", "--disable-extensions"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_github_issues(page, request)
            assert result.repo == request.repo
            assert len(result.issues) <= request.max_results
            print(f"\nTotal issues found: {len(result.issues)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_github_issues)
