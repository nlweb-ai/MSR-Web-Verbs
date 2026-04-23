"""
Auto-generated Playwright script (Python)
Overleaf – Copy Project

Searches for a project, opens it, and makes a copy via the editor
title dropdown menu.

Generated on: 2026-04-21T21:04:42.535Z
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
class OverleafCopyProjectRequest:
    search_query: str
    copy_name: str


@dataclass(frozen=True)
class OverleafCopyProjectResult:
    success: bool
    new_project_url: str
    error: str


# Searches for a project, opens it, and copies it with a new name.
def overleaf_copy_project(
    page: Page,
    request: OverleafCopyProjectRequest,
) -> OverleafCopyProjectResult:

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
        if project_links.count() == 0:
            return OverleafCopyProjectResult(
                success=False, new_project_url="",
                error=f'No projects found matching "{request.search_query}"',
            )
        checkpoint("Click first project link")
        project_links.first.click()
        page.wait_for_timeout(8000)
        print(f"  Opened: {page.url}")

        # ── STEP 4: Click title dropdown → Make a copy ───────────────
        print("STEP 4: Opening title dropdown...")
        title_btn = page.locator('button[aria-label="Project title options"]').first
        if title_btn.count() == 0:
            title_btn = page.locator('button:has-text("keyboard_arrow_down")').first
        checkpoint("Click project title dropdown")
        title_btn.click()
        page.wait_for_timeout(1000)

        print("STEP 5: Clicking Make a copy...")
        copy_link = page.locator('a:has-text("Make a copy")').first
        checkpoint("Click Make a copy")
        copy_link.click()
        page.wait_for_timeout(2000)
        print("  Copy dialog opened.")

        # ── STEP 6: Enter copy name and confirm ─────────────────────
        print(f'STEP 6: Entering copy name "{request.copy_name}"...')
        dialog = page.locator('[role="dialog"]')
        dialog.wait_for(state="visible", timeout=5000)
        name_input = dialog.locator('input[type="text"]').first
        checkpoint(f"Type copy name: {request.copy_name}")
        name_input.press("Control+a")
        name_input.type(request.copy_name, delay=30)
        page.wait_for_timeout(500)

        copy_btn = dialog.locator('button:has-text("Copy")')
        checkpoint("Click Copy button")
        copy_btn.click()
        page.wait_for_timeout(5000)

        # After copy, we should be redirected to the new project
        new_url = page.url
        print(f"  Copied. New URL: {new_url}")

        print(f"\nSuccess! Project copied. URL: {new_url}")
        return OverleafCopyProjectResult(
            success=True, new_project_url=new_url, error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return OverleafCopyProjectResult(
            success=False, new_project_url="", error=str(e),
        )


def test_overleaf_copy_project() -> None:
    print("=" * 60)
    print("  Overleaf – Copy Project")
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
            request = OverleafCopyProjectRequest(
                search_query="My Paper 1",
                copy_name="My Paper 1 (Copy)",
            )
            result = overleaf_copy_project(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.new_project_url}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_overleaf_copy_project)
