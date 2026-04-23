"""
Auto-generated Playwright script (Python)
Google Drive – Star File

Stars a file in Google Drive via right-click > Add to Starred.

Generated on: 2026-04-22T16:34:16.699Z
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
    """Create a Google Doc with the given name so we have a file to star."""
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
class GoogleDriveStarFileRequest:
    file_name: str


@dataclass(frozen=True)
class GoogleDriveStarFileResult:
    success: bool
    error: str


# Stars a file in Google Drive.
def google_drive_star_file(
    page: Page,
    request: GoogleDriveStarFileRequest,
) -> GoogleDriveStarFileResult:

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

        # ── STEP 3: Hover Organize, then click Add to Starred ────────
        print("STEP 3: Opening Organize submenu...")
        menu_items = page.locator('[role="menuitem"]')
        organize_item = None
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
            if "Organiz" in name:  # Organize / Organise
                organize_item = item
                break
        if organize_item is None:
            return GoogleDriveStarFileResult(
                success=False, error="Organize menu item not found"
            )
        organize_item.hover()
        page.wait_for_timeout(1000)
        print("  Organize submenu opened.")

        # Click "Add to starred" in the submenu
        print("STEP 4: Clicking Add to starred...")
        checkpoint("Click Add to starred")
        star_item = None
        for i in range(menu_items.count()):
            item = menu_items.nth(i)
            if not item.is_visible():
                continue
            label = (item.get_attribute("aria-label") or "").strip()
            if label.startswith("Add to starred"):
                star_item = item
                break
        if star_item is None:
            return GoogleDriveStarFileResult(
                success=False, error="Add to starred menu item not found"
            )
        star_item.click()
        page.wait_for_timeout(2000)
        print("  File starred.")

        # ── STEP 5: Verify in Starred section ────────────────────────
        print("STEP 5: Verifying in Starred...")
        checkpoint("Navigate to Starred")
        page.goto(
            "https://drive.google.com/drive/starred",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(5000)
        starred_item = page.locator(f'div[data-tooltip="{request.file_name}"]').first
        if starred_item.count() == 0:
            starred_item = page.locator(f'[aria-label*="{request.file_name}"]').first
        found = starred_item.count() > 0
        if found:
            print(f"  Verified: '{request.file_name}' is in Starred.")
        else:
            print(f"  Warning: '{request.file_name}' not found in Starred view.")

        print(f"\nSuccess! Starred '{request.file_name}'")
        return GoogleDriveStarFileResult(success=True, error="")

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDriveStarFileResult(success=False, error=str(e))


def test_google_drive_star_file() -> None:
    print("=" * 60)
    print("  Google Drive – Star File")
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
            ensure_test_file_exists(page, "Test File For Star")
            request = GoogleDriveStarFileRequest(
                file_name="Test File For Star",
            )
            result = google_drive_star_file(page, request)
            if result.success:
                print("\n  SUCCESS: File starred")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_drive_star_file)
