"""
Auto-generated Playwright script (Python)
Overleaf – Rename Project

Searches for a project, opens it, and renames it via the editor
title dropdown menu.

Generated on: 2026-04-21T21:03:50.884Z
Recorded 2 browser interactions

Uses the user's Chrome profile for persistent login state.
"""

import os
import re
import importlib.util
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


def ensure_test_project_exists(page: Page, project_name: str = "My Paper 1") -> str:
    """Check if a project exists on the Overleaf dashboard. If not, create one.

    Returns the project_id extracted from the project URL.
    """
    page.goto(
        "https://www.overleaf.com/project",
        wait_until="domcontentloaded",
        timeout=30000,
    )
    page.wait_for_timeout(3000)

    search_input = page.locator(
        'input[placeholder="Search in all projects\u2026"]'
    ).first
    search_input.click()
    page.wait_for_timeout(500)
    search_input.press("Control+a")
    search_input.type(project_name, delay=50)
    page.wait_for_timeout(2000)

    links = page.locator('td a[href^="/project/"]')
    if links.count() > 0:
        href = links.first.get_attribute("href")
        project_id = href.split("/project/")[-1]
        print(f"  Project '{project_name}' found (id={project_id})")
        return project_id

    print(f"  Project '{project_name}' not found, creating...")
    spec = importlib.util.spec_from_file_location(
        "create_proj",
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "overleaf_com__createProject",
            "overleaf_create_project.py",
        ),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    result = mod.create_overleaf_project(
        page,
        mod.OverleafCreateProjectRequest(
            template_query="ieee conference",
            project_name=project_name,
        ),
    )
    if not result.success:
        raise RuntimeError(f"Failed to create project: {result.error}")
    project_id = result.project_url.split("/project/")[-1]
    print(f"  Created project '{project_name}' (id={project_id})")
    return project_id


@dataclass(frozen=True)
class OverleafRenameProjectRequest:
    search_query: str
    new_name: str


@dataclass(frozen=True)
class OverleafRenameProjectResult:
    success: bool
    project_url: str
    error: str


# Searches for a project on the dashboard, opens it, and renames it.
def overleaf_rename_project(
    page: Page,
    request: OverleafRenameProjectRequest,
) -> OverleafRenameProjectResult:

    try:
        # ── STEP 1: Navigate to project dashboard ────────────────────
        print("STEP 1: Loading Overleaf project dashboard...")
        checkpoint("Navigate to project dashboard")
        page.goto(
            "https://www.overleaf.com/project",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(2000)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Search for project ───────────────────────────────
        print(f'STEP 2: Searching for "{request.search_query}"...')
        search_input = page.locator(
            'input[placeholder="Search in all projects\u2026"]'
        ).first
        checkpoint("Click search input")
        search_input.click()
        page.wait_for_timeout(500)
        search_input.press("Control+a")
        checkpoint(f"Type search query: {request.search_query}")
        search_input.type(request.search_query, delay=50)
        page.wait_for_timeout(2000)
        print("  Search entered.")

        # ── STEP 3: Click the first matching project ─────────────────
        print("STEP 3: Clicking first matching project...")
        project_links = page.locator('td a[href^="/project/"]')
        count = project_links.count()
        if count == 0:
            return OverleafRenameProjectResult(
                success=False, project_url="",
                error=f'No projects found matching "{request.search_query}"',
            )
        checkpoint("Click first project link")
        project_links.first.click()
        page.wait_for_timeout(8000)
        print(f"  Opened: {page.url}")

        # ── STEP 4: Click the project title dropdown ─────────────────
        print("STEP 4: Opening title dropdown...")
        title_btn = page.locator('button[aria-label="Project title options"]').first
        if title_btn.count() == 0:
            title_btn = page.locator('button:has-text("keyboard_arrow_down")').first
        checkpoint("Click project title dropdown")
        title_btn.click()
        page.wait_for_timeout(1000)
        print("  Dropdown opened.")

        # ── STEP 5: Click Rename ─────────────────────────────────────
        print("STEP 5: Clicking Rename...")
        rename_link = page.locator('a:has-text("Rename")').first
        checkpoint("Click Rename")
        rename_link.click()
        page.wait_for_timeout(1000)
        print("  Rename mode active.")

        # ── STEP 6: Type new name and confirm ────────────────────────
        print(f'STEP 6: Typing new name "{request.new_name}"...')
        name_input = page.locator(
            'input.ide-redesign-toolbar-editable-project-name'
        ).first
        checkpoint(f"Type new name: {request.new_name}")
        name_input.press("Control+a")
        name_input.type(request.new_name, delay=30)
        name_input.press("Enter")
        page.wait_for_timeout(2000)
        print(f"  Renamed to: {request.new_name}")

        project_url = page.url
        print(f"\nSuccess! Project renamed. URL: {project_url}")
        return OverleafRenameProjectResult(
            success=True, project_url=project_url, error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return OverleafRenameProjectResult(
            success=False, project_url="", error=str(e),
        )


def test_overleaf_rename_project() -> None:
    print("=" * 60)
    print("  Overleaf – Rename Project")
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
            ensure_test_project_exists(page, "My Paper 1")
            request = OverleafRenameProjectRequest(
                search_query="My Paper 1",
                new_name="My Renamed Paper",
            )
            result = overleaf_rename_project(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.project_url}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_overleaf_rename_project)
