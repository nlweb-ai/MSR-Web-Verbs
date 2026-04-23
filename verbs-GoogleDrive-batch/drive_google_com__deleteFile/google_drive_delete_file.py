"""
Auto-generated Playwright script (Python)
Google Drive – Delete File

Moves a file to trash in Google Drive via right-click > Move to trash.

Generated on: 2026-04-22T16:34:08.992Z
Recorded 3 browser interactions

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
    """Create a Google Doc with the given name so we have a file to delete."""
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
class GoogleDriveDeleteFileRequest:
    file_name: str


@dataclass(frozen=True)
class GoogleDriveDeleteFileResult:
    success: bool
    error: str


# Moves a file to trash in Google Drive.
def google_drive_delete_file(
    page: Page,
    request: GoogleDriveDeleteFileRequest,
) -> GoogleDriveDeleteFileResult:

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
        print(f'STEP 2: Right-clicking on "{request.file_name}"...')
        file_item = page.locator(f'div[data-tooltip="{request.file_name}"]').first
        if file_item.count() == 0:
            file_item = page.locator(f'[aria-label*="{request.file_name}"]').first
        checkpoint(f"Right-click file: {request.file_name}")
        file_item.click(button="right")
        page.wait_for_timeout(1500)
        print("  Context menu opened.")

        # ── STEP 3: Click Move to trash ──────────────────────────────
        print("STEP 3: Clicking Move to trash...")
        trash_item = page.locator('[role="menuitem"]:has-text("Move to trash")').first
        if trash_item.count() == 0:
            trash_item = page.locator('div:has-text("Move to trash")').first
        checkpoint("Click Move to trash")
        trash_item.click()
        page.wait_for_timeout(3000)
        print("  File moved to trash.")

        print(f"\nSuccess! Moved '{request.file_name}' to trash.")
        return GoogleDriveDeleteFileResult(success=True, error="")

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDriveDeleteFileResult(success=False, error=str(e))


def test_google_drive_delete_file() -> None:
    print("=" * 60)
    print("  Google Drive – Delete File")
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
            ensure_test_file_exists(page, "Test File For Delete")
            request = GoogleDriveDeleteFileRequest(
                file_name="Test File For Delete",
            )
            result = google_drive_delete_file(page, request)
            if result.success:
                print("\n  SUCCESS: File deleted")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_drive_delete_file)
