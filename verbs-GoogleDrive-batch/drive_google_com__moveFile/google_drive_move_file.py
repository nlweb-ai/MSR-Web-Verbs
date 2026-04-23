"""
Auto-generated Playwright script (Python)
Google Drive – Move File

Moves a file to a different folder in Google Drive via right-click > Organise.

Generated on: 2026-04-22T16:34:13.527Z
Recorded 5 browser interactions

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
    """Create a Google Doc with the given name so we have a file to move."""
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


def ensure_test_folder_exists(page: Page, folder_name: str) -> None:
    """Create a folder in Google Drive if it doesn't already exist."""
    page.goto("https://drive.google.com/drive/my-drive", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    # Check if folder already exists
    existing = page.locator(f'div[data-tooltip="{folder_name}"]').first
    if existing.count() > 0:
        print(f"  Folder '{folder_name}' already exists")
        return
    # Create new folder
    new_btn = page.locator('button:has-text("New")').first
    if new_btn.count() == 0:
        new_btn = page.locator('[aria-label="New"]').first
    new_btn.click()
    page.wait_for_timeout(1500)
    folder_item = page.locator('[role="menuitem"]:has-text("New folder")').first
    folder_item.click()
    page.wait_for_timeout(2000)
    name_input = page.locator('input[type="text"]').last
    name_input.click()
    name_input.press("Control+a")
    name_input.type(folder_name, delay=30)
    page.wait_for_timeout(500)
    create_btn = page.locator('button:has-text("Create")').first
    create_btn.click()
    page.wait_for_timeout(3000)
    print(f"  Created folder '{folder_name}'")


@dataclass(frozen=True)
class GoogleDriveMoveFileRequest:
    file_name: str
    destination_folder: str


@dataclass(frozen=True)
class GoogleDriveMoveFileResult:
    success: bool
    destination_folder: str
    error: str


# Moves a file to a different folder in Google Drive.
def google_drive_move_file(
    page: Page,
    request: GoogleDriveMoveFileRequest,
) -> GoogleDriveMoveFileResult:

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

        # ── STEP 3: Hover over Organise to reveal submenu ─────────
        print("STEP 3: Opening Organise submenu...")
        organise_item = page.locator('[role="menuitem"]:has-text("Organise")').first
        if organise_item.count() == 0 or not organise_item.is_visible():
            organise_item = page.locator('[role="menuitem"]:has-text("Organize")').first
        if organise_item.count() == 0 or not organise_item.is_visible():
            organise_item = page.locator('[role="menuitem"]:has-text("Move to")').first
        checkpoint("Hover over Organise")
        organise_item.hover()
        page.wait_for_timeout(2000)

        # Collect all menuitems for submenu scanning
        all_items = page.locator('[role="menuitem"]')
        print("  Submenu revealed.")

        # ── STEP 4: Click Move in the submenu ────────────────────────
        print("STEP 4: Clicking Move...")
        move_clicked = False
        for i in range(all_items.count()):
            item = all_items.nth(i)
            if not item.is_visible():
                continue
            label = item.get_attribute("aria-label") or ""
            # Match "Move Ctrl+Alt+M" but NOT "Move to trash"
            if label.startswith("Move") and "trash" not in label.lower():
                checkpoint("Click Move submenu")
                item.click()
                move_clicked = True
                print(f"  Clicked item with label='{label}'")
                break
        if not move_clicked:
            print("  WARNING: Could not find Move submenu item, trying keyboard shortcut")
            page.keyboard.press("Control+Alt+m")
        page.wait_for_timeout(4000)
        print("  Move dialog should be open.")

        # ── STEP 5: Search for destination folder inside picker iframe ─
        print(f'STEP 5: Searching for "{request.destination_folder}" in picker...')
        checkpoint(f"Search folder: {request.destination_folder}")
        # The Move dialog is an iframe (drive.google.com/picker/minpick)
        picker = page.frame_locator('iframe[src*="picker"]')
        # Click the search button / icon inside the picker
        search_btn = picker.locator('[aria-label="Search"]').first
        if search_btn.count() == 0:
            search_btn = picker.locator('img[alt="Search"]').first
        if search_btn.count() == 0:
            search_btn = picker.locator('[data-tooltip="Search"]').first
        if search_btn.count() == 0:
            # Try any clickable search icon
            search_btn = picker.locator('div.Chn84b-r4nke').first
        search_btn.click()
        page.wait_for_timeout(1500)

        # Type the folder name in the search input
        search_input = picker.locator('input[type="text"]').first
        if search_input.count() == 0:
            search_input = picker.locator('input[aria-label="Search"]').first
        if search_input.count() == 0:
            search_input = picker.locator('input').first
        search_input.click()
        search_input.type(request.destination_folder, delay=30)
        page.wait_for_timeout(500)
        search_input.press("Enter")
        page.wait_for_timeout(4000)
        print(f"  Search results loaded.")

        # ── STEP 6: Select the folder from search results ────────────
        print(f'STEP 6: Selecting "{request.destination_folder}"...')
        checkpoint(f"Select folder: {request.destination_folder}")
        # Click the folder in the search results
        folder_item = picker.locator(f'text="{request.destination_folder}"').first
        if folder_item.count() == 0:
            folder_item = picker.locator(f'div:has-text("{request.destination_folder}")').first
        folder_item.click()
        page.wait_for_timeout(1500)
        print(f"  Selected: {request.destination_folder}")

        # ── STEP 7: Confirm move ─────────────────────────────────────
        print("STEP 7: Confirming move...")
        checkpoint("Click Move here")
        # The "Move here" button can be inside the picker iframe or in the parent
        move_btn = picker.locator('button:has-text("Move here")').first
        if move_btn.count() == 0:
            move_btn = picker.locator('button:has-text("Move")').first
        if move_btn.count() == 0:
            # Try parent page
            move_btn = page.locator('button:has-text("Move here")').first
        if move_btn.count() == 0:
            move_btn = page.locator('button:has-text("Move")').first
        move_btn.click()
        page.wait_for_timeout(3000)
        print("  File moved.")

        print(f"\nSuccess! Moved to {request.destination_folder}")
        return GoogleDriveMoveFileResult(
            success=True,
            destination_folder=request.destination_folder,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDriveMoveFileResult(
            success=False, destination_folder="", error=str(e),
        )


def test_google_drive_move_file() -> None:
    print("=" * 60)
    print("  Google Drive – Move File")
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
            ensure_test_file_exists(page, "Test File For Move")
            ensure_test_folder_exists(page, "Test Move Destination")
            request = GoogleDriveMoveFileRequest(
                file_name="Test File For Move",
                destination_folder="Test Move Destination",
            )
            result = google_drive_move_file(page, request)
            if result.success:
                print(f"\n  SUCCESS: Moved to {result.destination_folder}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_drive_move_file)
