"""
Auto-generated Playwright script (Python)
Google Drive – Upload File

Uploads a file to Google Drive via the "+ New" button > "File upload".

Generated on: 2026-04-22T16:34:04.729Z
Recorded 4 browser interactions

Uses the user's Chrome profile for persistent login state.
"""

import os
import tempfile
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GoogleDriveUploadFileRequest:
    file_path: str  # local path to the file to upload


@dataclass(frozen=True)
class GoogleDriveUploadFileResult:
    success: bool
    uploaded_file_name: str
    error: str


# Uploads a file to Google Drive via the UI.
def google_drive_upload_file(
    page: Page,
    request: GoogleDriveUploadFileRequest,
) -> GoogleDriveUploadFileResult:

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

        # ── STEP 3: Click "File upload" ──────────────────────────────
        print("STEP 3: Clicking File upload...")
        # Set up file chooser listener before clicking
        file_name = os.path.basename(request.file_path)
        with page.expect_file_chooser() as fc_info:
            # Drive keeps hidden/disabled duplicates — find the visible one
            menu_items = page.locator('[role="menuitem"]')
            file_upload_item = None
            for i in range(menu_items.count()):
                item = menu_items.nth(i)
                if not item.is_visible():
                    continue
                label = (item.get_attribute("aria-label") or "").strip()
                text = ""
                try:
                    text = item.inner_text(timeout=500).strip()
                except Exception:
                    pass
                name = label if label else text
                if "File upload" in name:
                    file_upload_item = item
                    break
            if file_upload_item is None:
                return GoogleDriveUploadFileResult(
                    success=False, uploaded_file_name="",
                    error="File upload menu item not found",
                )
            checkpoint("Click File upload")
            file_upload_item.click()
        file_chooser = fc_info.value
        file_chooser.set_files(request.file_path)
        page.wait_for_timeout(2000)
        print(f"  File selected: {file_name}")

        # ── STEP 4: Wait for upload to complete ──────────────────────
        print("STEP 4: Waiting for upload to complete...")
        checkpoint("Wait for upload to complete")
        # Wait for the upload notification to appear and complete
        page.wait_for_timeout(5000)
        print(f"  Upload complete: {file_name}")

        print(f"\nSuccess! Uploaded {file_name}")
        return GoogleDriveUploadFileResult(
            success=True,
            uploaded_file_name=file_name,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDriveUploadFileResult(
            success=False, uploaded_file_name="", error=str(e),
        )


def test_google_drive_upload_file() -> None:
    print("=" * 60)
    print("  Google Drive – Upload File")
    print("=" * 60)

    # Create a small temp file to upload
    tmp_dir = tempfile.mkdtemp()
    test_file = os.path.join(tmp_dir, "test_upload.txt")
    with open(test_file, "w") as f:
        f.write("This is a test file for Google Drive upload.")

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
            request = GoogleDriveUploadFileRequest(
                file_path=test_file,
            )
            result = google_drive_upload_file(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.uploaded_file_name}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()

    # Clean up temp file
    try:
        os.remove(test_file)
        os.rmdir(tmp_dir)
    except:
        pass


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_drive_upload_file)
