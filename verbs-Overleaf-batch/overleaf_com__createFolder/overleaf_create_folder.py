"""
Auto-generated Playwright script (Python)
Overleaf – Create Folder

Navigates to a project by ID and creates a new folder
in the file tree sidebar.

Generated on: 2026-04-21T21:05:32.514Z
Recorded 4 browser interactions

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
class OverleafCreateFolderRequest:
    project_id: str
    folder_name: str


@dataclass(frozen=True)
class OverleafCreateFolderResult:
    success: bool
    folder_name: str
    error: str


# Navigates to a project by ID and creates a new folder in the file tree.
def overleaf_create_folder(
    page: Page,
    request: OverleafCreateFolderRequest,
) -> OverleafCreateFolderResult:

    try:
        # ── STEP 1: Navigate to project editor ──────────────────────
        print("STEP 1: Loading project editor...")
        checkpoint("Navigate to project editor")
        page.goto(
            f"https://www.overleaf.com/project/{request.project_id}",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(8000)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Click New Folder button ──────────────────────────
        print("STEP 2: Clicking New Folder button...")
        folder_btn = page.locator('button:has-text("create_new_folder")').first
        checkpoint("Click New Folder button")
        folder_btn.click()
        page.wait_for_timeout(1000)
        print("  New folder dialog opened.")

        # ── STEP 3: Enter folder name ────────────────────────────────
        print(f'STEP 3: Entering folder name "{request.folder_name}"...')
        name_input = page.locator('#folder-name').first
        checkpoint(f"Type folder name: {request.folder_name}")
        name_input.press("Control+a")
        name_input.type(request.folder_name, delay=30)
        page.wait_for_timeout(500)
        print("  Name entered.")

        # ── STEP 4: Confirm folder creation ──────────────────────────
        print("STEP 4: Confirming folder creation...")
        create_btn = page.locator('.modal-footer .btn-primary').first
        checkpoint("Click Create button")
        create_btn.click()
        page.wait_for_timeout(2000)
        print(f"  Folder created: {request.folder_name}")

        print(f"\nSuccess! Created folder: {request.folder_name}")
        return OverleafCreateFolderResult(
            success=True, folder_name=request.folder_name, error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return OverleafCreateFolderResult(
            success=False, folder_name="", error=str(e),
        )


def test_overleaf_create_folder() -> None:
    print("=" * 60)
    print("  Overleaf – Create Folder")
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
            project_id = ensure_test_project_exists(page, "My Paper 1")
            request = OverleafCreateFolderRequest(
                project_id=project_id,
                folder_name="test_folder",
            )
            result = overleaf_create_folder(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.folder_name}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_overleaf_create_folder)
