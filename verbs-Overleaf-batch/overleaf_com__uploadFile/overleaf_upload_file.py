"""
Auto-generated Playwright script (Python)
Overleaf – Upload File

Navigates to a project by ID and uploads a local file
using the file tree sidebar Upload button and file chooser API.

Generated on: 2026-04-21T21:05:06.897Z
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
class OverleafUploadFileRequest:
    project_id: str
    local_file_path: str


@dataclass(frozen=True)
class OverleafUploadFileResult:
    success: bool
    uploaded_file_name: str
    error: str


# Navigates to a project by ID and uploads a local file.
def overleaf_upload_file(
    page: Page,
    request: OverleafUploadFileRequest,
) -> OverleafUploadFileResult:

    try:
        if not os.path.isfile(request.local_file_path):
            return OverleafUploadFileResult(
                success=False, uploaded_file_name="",
                error=f"File not found: {request.local_file_path}",
            )

        file_name = os.path.basename(request.local_file_path)

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

        # ── STEP 2: Click Upload button in file tree ─────────────────
        print("STEP 2: Clicking Upload button...")
        upload_btn = page.locator('button[aria-label="Upload"]').first
        if upload_btn.count() == 0:
            upload_btn = page.locator('button:has-text("upload")').first
        checkpoint("Click Upload button")
        with page.expect_file_chooser() as fc_info:
            upload_btn.click()
        file_chooser = fc_info.value
        page.wait_for_timeout(1000)
        print("  File chooser opened.")

        # ── STEP 3: Set the file ─────────────────────────────────────
        print(f"STEP 3: Uploading {file_name}...")
        checkpoint(f"Upload file: {file_name}")
        file_chooser.set_files(request.local_file_path)
        page.wait_for_timeout(3000)
        print(f"  File uploaded: {file_name}")

        print(f"\nSuccess! Uploaded: {file_name}")
        return OverleafUploadFileResult(
            success=True, uploaded_file_name=file_name, error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return OverleafUploadFileResult(
            success=False, uploaded_file_name="", error=str(e),
        )


def test_overleaf_upload_file() -> None:
    print("=" * 60)
    print("  Overleaf – Upload File")
    print("=" * 60)

    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default",
    )

    # Create a test file if it doesn't exist
    test_file = os.path.join(os.environ["USERPROFILE"], "Downloads", "test_upload.txt")
    if not os.path.exists(test_file):
        with open(test_file, "w") as f:
            f.write("This is a test upload file for Overleaf.\n")

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
            request = OverleafUploadFileRequest(
                project_id=project_id,
                local_file_path=test_file,
            )
            result = overleaf_upload_file(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.uploaded_file_name}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_overleaf_upload_file)
