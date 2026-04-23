"""
Auto-generated Playwright script (Python)
Overleaf – Delete Project

Searches for an Overleaf project by name on the dashboard,
selects it, moves it to trash, and confirms the deletion.

Generated on: 2026-04-21T21:02:45.563Z
Recorded 3 browser interactions

Uses the user's Chrome profile for persistent login state.
"""

import os
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
class OverleafDeleteProjectRequest:
    search_query: str


@dataclass(frozen=True)
class OverleafDeleteProjectResult:
    success: bool
    error: str


# Searches for a project by name on the Overleaf dashboard,
# selects it, clicks the trash button, and confirms deletion.
def overleaf_delete_project(
    page: Page,
    request: OverleafDeleteProjectRequest,
) -> OverleafDeleteProjectResult:

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

        # ── STEP 3: Select the first matching project ────────────────
        print("STEP 3: Selecting first matching project...")
        first_checkbox = page.locator('td input[type="checkbox"]').first
        if first_checkbox.count() == 0:
            return OverleafDeleteProjectResult(
                success=False,
                error=f'No projects found matching "{request.search_query}"',
            )
        checkpoint("Click project checkbox")
        first_checkbox.click()
        page.wait_for_timeout(1000)
        print("  Project selected.")

        # ── STEP 4: Click the trash button ───────────────────────────
        print("STEP 4: Clicking trash button...")
        trash_btn = page.locator('button:has-text("delete")').first
        checkpoint("Click trash button")
        trash_btn.click()
        page.wait_for_timeout(2000)
        print("  Trash dialog opened.")

        # ── STEP 5: Confirm deletion ─────────────────────────────────
        print("STEP 5: Confirming deletion...")
        dialog = page.locator('[role="dialog"]')
        dialog.wait_for(state="visible", timeout=5000)
        confirm_btn = dialog.locator('button:has-text("Confirm")')
        checkpoint("Click Confirm in dialog")
        confirm_btn.click()
        page.wait_for_timeout(2000)
        print("  Deletion confirmed.")

        print("\nSuccess! Project moved to trash.")
        return OverleafDeleteProjectResult(success=True, error="")

    except Exception as e:
        print(f"Error: {e}")
        return OverleafDeleteProjectResult(success=False, error=str(e))


def test_overleaf_delete_project() -> None:
    print("=" * 60)
    print("  Overleaf – Delete Project")
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
            request = OverleafDeleteProjectRequest(
                search_query="My Paper 1",
            )
            result = overleaf_delete_project(page, request)
            if result.success:
                print("\n  SUCCESS: Project deleted")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_overleaf_delete_project)
