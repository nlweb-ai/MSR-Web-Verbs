"""
Auto-generated Playwright script (Python)
Google Drive – Rename File

Renames a file in Google Drive via right-click context menu > Rename.

Generated on: 2026-04-22T16:34:07.599Z
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


def ensure_test_file_exists(page: Page, file_name: str) -> None:
    """Create a Google Doc with the given name so we have a file to rename."""
    page.goto("https://docs.google.com/document/create", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    title_input = page.locator('input[aria-label="Rename"]').first
    title_input.click()
    page.wait_for_timeout(500)
    title_input.press("Control+a")
    title_input.type(file_name, delay=30)
    title_input.press("Enter")
    page.wait_for_timeout(2000)
    print(f"  Created test file '{file_name}'")


@dataclass(frozen=True)
class GoogleDriveRenameFileRequest:
    current_name: str
    new_name: str


@dataclass(frozen=True)
class GoogleDriveRenameFileResult:
    success: bool
    new_name: str
    error: str


# Renames a file in Google Drive.
def google_drive_rename_file(
    page: Page,
    request: GoogleDriveRenameFileRequest,
) -> GoogleDriveRenameFileResult:

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

        # ── STEP 2: Right-click the file ─────────────────────────────
        print(f'STEP 2: Right-clicking on "{request.current_name}"...')
        file_item = page.locator(f'div[data-tooltip="{request.current_name}"]').first
        if file_item.count() == 0:
            file_item = page.locator(f'[aria-label*="{request.current_name}"]').first
        checkpoint(f"Right-click file: {request.current_name}")
        file_item.click(button="right")
        page.wait_for_timeout(1500)
        print("  Context menu opened.")

        # ── STEP 3: Click Rename ─────────────────────────────────────
        print("STEP 3: Clicking Rename...")
        rename_item = page.locator('[role="menuitem"]:has-text("Rename")').first
        if rename_item.count() == 0:
            rename_item = page.locator('div:has-text("Rename")').first
        checkpoint("Click Rename")
        rename_item.click()
        page.wait_for_timeout(1500)
        print("  Rename input active.")

        # ── STEP 4: Enter new name ───────────────────────────────────
        print(f'STEP 4: Entering new name "{request.new_name}"...')
        # The rename input should be focused; type directly
        rename_input = page.locator('input[type="text"]:focus').first
        if rename_input.count() == 0:
            rename_input = page.locator('[aria-label="Rename"]').first
        if rename_input.count() == 0:
            rename_input = page.locator('input[type="text"]').last
        checkpoint(f"Type new name: {request.new_name}")
        rename_input.press("Control+a")
        rename_input.type(request.new_name, delay=30)
        page.wait_for_timeout(500)

        # Confirm by clicking OK or pressing Enter
        ok_btn = page.locator('button:has-text("OK")').first
        if ok_btn.count() > 0:
            ok_btn.click()
        else:
            rename_input.press("Enter")
        page.wait_for_timeout(2000)
        print(f"  Renamed to: {request.new_name}")

        print(f"\nSuccess! Renamed to {request.new_name}")
        return GoogleDriveRenameFileResult(
            success=True,
            new_name=request.new_name,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDriveRenameFileResult(
            success=False, new_name="", error=str(e),
        )


def test_google_drive_rename_file() -> None:
    print("=" * 60)
    print("  Google Drive – Rename File")
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
            ensure_test_file_exists(page, "Test File For Rename")
            request = GoogleDriveRenameFileRequest(
                current_name="Test File For Rename",
                new_name="Renamed File",
            )
            result = google_drive_rename_file(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.new_name}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_drive_rename_file)
