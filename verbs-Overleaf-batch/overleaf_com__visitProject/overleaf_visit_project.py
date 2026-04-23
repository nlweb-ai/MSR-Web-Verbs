"""
Playwright script (Python) — Overleaf Visit Project

Searches for a project on the Overleaf dashboard and opens it in the LaTeX editor.

Uses the user's Chrome profile for persistent login state.
"""

import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class OverleafVisitProjectRequest:
    search_query: str


@dataclass(frozen=True)
class OverleafVisitProjectResult:
    success: bool
    project_url: str
    error: str


# Searches for a project by name on the Overleaf dashboard (/project),
# clicks the first matching result, and navigates to the LaTeX editor.
# Returns the project URL on success.
def visit_overleaf_project(
    page: Page,
    request: OverleafVisitProjectRequest,
) -> OverleafVisitProjectResult:

    try:
        # ── STEP 1: Navigate to Overleaf project dashboard ───────────
        print("STEP 1: Loading Overleaf project dashboard...")
        checkpoint("Navigate to project dashboard")
        page.goto("https://www.overleaf.com/project", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Search for project ───────────────────────────────
        print(f'STEP 2: Searching for "{request.search_query}"...')
        search_input = page.locator('input[placeholder="Search in all projects\u2026"]').first
        checkpoint("Click search input")
        search_input.click()
        page.wait_for_timeout(500)
        search_input.press("Control+a")
        checkpoint(f"Type search query: {request.search_query}")
        search_input.type(request.search_query, delay=50)
        page.wait_for_timeout(2000)
        print("  Search entered, waiting for results...")

        # ── STEP 3: Click the first matching project ─────────────────
        print("STEP 3: Clicking first matching project...")
        project_links = page.locator('td a[href^="/project/"]')
        count = project_links.count()
        print(f"  Found {count} project link(s)")

        if count == 0:
            return OverleafVisitProjectResult(
                success=False, project_url="",
                error=f'No projects found matching "{request.search_query}"',
            )

        first_link = project_links.first
        project_name = first_link.inner_text(timeout=2000).strip()
        print(f'  Clicking: "{project_name}"')
        checkpoint(f"Click project: {project_name}")
        first_link.click()
        page.wait_for_timeout(5000)

        project_url = page.url
        print(f"  Project URL: {project_url}")

        # ── STEP 4: Verify we landed on the project editor ──────────
        if "/project/" not in project_url:
            return OverleafVisitProjectResult(
                success=False, project_url="",
                error=f"Did not navigate to project editor: {project_url}",
            )

        title = page.title()
        print(f"  Page title: {title}")
        print(f"\nSuccess! Project URL: {project_url}")
        return OverleafVisitProjectResult(success=True, project_url=project_url, error="")

    except Exception as e:
        print(f"Error: {e}")
        return OverleafVisitProjectResult(success=False, project_url="", error=str(e))


def test_visit_overleaf_project() -> None:
    request = OverleafVisitProjectRequest(
        search_query="My paper",
    )

    print("=" * 60)
    print("  Overleaf – Visit Project")
    print(f"  Search: {request.search_query}")
    print("=" * 60)

    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default",
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=False,
            viewport=None,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
                "--start-maximized",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = visit_overleaf_project(page, request)
            assert result.success, f"Visit project failed: {result.error}"
            print(f"\n  SUCCESS: Opened project at {result.project_url}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_visit_overleaf_project)
