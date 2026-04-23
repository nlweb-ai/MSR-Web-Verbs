"""
Auto-generated Playwright script (Python)
Google Drive – Create Folder

Creates a new folder in Google Drive via "+ New" > "New folder".

Generated on: 2026-04-22T16:34:06.115Z
Recorded 4 browser interactions

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
class GoogleDriveCreateFolderRequest:
    folder_name: str


@dataclass(frozen=True)
class GoogleDriveCreateFolderResult:
    success: bool
    folder_name: str
    error: str


# Creates a new folder in Google Drive.
def google_drive_create_folder(
    page: Page,
    request: GoogleDriveCreateFolderRequest,
) -> GoogleDriveCreateFolderResult:

    try:
        # ── STEP 1: Navigate to My Drive ─────────────────────────────
        print("STEP 1: Navigating to Google Drive...")
        checkpoint("Navigate to My Drive")
        page.goto(
            "https://drive.google.com/drive/my-drive",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(5000)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Click "+ New" button ─────────────────────────────
        print("STEP 2: Clicking + New button...")
        new_btn = page.locator('button:has-text("New")').first
        if new_btn.count() == 0:
            new_btn = page.locator('[aria-label="New"]').first
        checkpoint("Click + New button")
        new_btn.click()
        page.wait_for_timeout(1500)
        print("  + New menu opened.")

        # ── STEP 3: Click "New folder" ───────────────────────────────
        print("STEP 3: Clicking New folder...")
        folder_item = page.locator('[role="menuitem"]:has-text("New folder")').first
        if folder_item.count() == 0:
            folder_item = page.locator('div:has-text("New folder")').first
        checkpoint("Click New folder")
        folder_item.click()
        page.wait_for_timeout(2000)
        print("  New folder dialog opened.")

        # ── STEP 4: Enter folder name and confirm ────────────────────
        print(f'STEP 4: Entering folder name "{request.folder_name}"...')
        name_input = page.locator('input[type="text"]').last
        if name_input.count() == 0:
            name_input = page.locator('[aria-label="Folder name"]').first
        checkpoint(f"Type folder name: {request.folder_name}")
        name_input.click()
        name_input.press("Control+a")
        name_input.type(request.folder_name, delay=30)
        page.wait_for_timeout(500)

        # Click Create button
        create_btn = page.locator('button:has-text("Create")').first
        checkpoint("Click Create")
        create_btn.click()
        page.wait_for_timeout(3000)
        print(f"  Folder created: {request.folder_name}")

        print(f"\nSuccess! Created folder: {request.folder_name}")
        return GoogleDriveCreateFolderResult(
            success=True,
            folder_name=request.folder_name,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDriveCreateFolderResult(
            success=False, folder_name="", error=str(e),
        )


def test_google_drive_create_folder() -> None:
    print("=" * 60)
    print("  Google Drive – Create Folder")
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
            request = GoogleDriveCreateFolderRequest(
                folder_name="Test Folder 1",
            )
            result = google_drive_create_folder(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.folder_name}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_drive_create_folder)
