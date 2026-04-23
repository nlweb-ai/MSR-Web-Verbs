"""
Auto-generated Playwright script (Python)
Google Drive – Share File

Shares a file in Google Drive via right-click > Share with an email address.

Generated on: 2026-04-22T16:34:10.410Z
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
    """Create a Google Doc with the given name so we have a file to share."""
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
class GoogleDriveShareFileRequest:
    file_name: str
    email: str
    permission: str  # "Editor", "Viewer", or "Commenter"


@dataclass(frozen=True)
class GoogleDriveShareFileResult:
    success: bool
    error: str


# Shares a file in Google Drive with an email address.
def google_drive_share_file(
    page: Page,
    request: GoogleDriveShareFileRequest,
) -> GoogleDriveShareFileResult:

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

        # ── STEP 3: Click Share > Share ──────────────────────────────
        print("STEP 3: Clicking Share...")
        # Google Drive keeps hidden/disabled duplicates of menu items.
        # The visible Share item often has an empty aria-label; match by inner text.
        menu_items = page.locator('[role="menuitem"]')
        share_parent = None
        for i in range(menu_items.count()):
            item = menu_items.nth(i)
            if not item.is_visible():
                continue
            if item.get_attribute("aria-disabled") == "true":
                continue
            label = (item.get_attribute("aria-label") or "").strip()
            text = ""
            try:
                text = item.inner_text(timeout=500).strip()
            except Exception:
                pass
            name = label if label else text
            if name.startswith("Share"):
                share_parent = item
                break
        if share_parent is None:
            return GoogleDriveShareFileResult(
                success=False, error="Share menu item not found"
            )
        checkpoint("Click Share")
        # Share is a submenu parent — hover to reveal, then click the
        # leaf "Share" item (not "Copy link").
        share_parent.hover()
        page.wait_for_timeout(1000)
        # Re-scan for visible Share leaf item (no aria-haspopup)
        leaf_found = False
        for i in range(menu_items.count()):
            item = menu_items.nth(i)
            if not item.is_visible():
                continue
            if item.get_attribute("aria-disabled") == "true":
                continue
            label = (item.get_attribute("aria-label") or "").strip()
            text = ""
            try:
                text = item.inner_text(timeout=500).strip()
            except Exception:
                pass
            name = label if label else text
            if name.startswith("Share") and item.get_attribute("aria-haspopup") != "true":
                item.click()
                leaf_found = True
                break
        if not leaf_found:
            # Fallback: click the parent directly
            share_parent.click()
        page.wait_for_timeout(2000)
        print("  Share dialog opened.")

        # ── STEP 4: Enter email in the share dialog ──────────────────
        print(f'STEP 4: Entering email "{request.email}"...')
        # The share dialog is in an iframe
        share_frame = page.frame_locator('iframe[src*="drivesharing"]')
        email_input = share_frame.locator('input[aria-label="Add people, groups, and calendar events"]').first
        if email_input.count() == 0:
            email_input = share_frame.locator('input[type="text"]').first
        checkpoint(f"Enter email: {request.email}")
        email_input.click()
        email_input.type(request.email, delay=30)
        page.wait_for_timeout(1500)
        email_input.press("Enter")
        page.wait_for_timeout(1500)
        print("  Email entered.")

        # ── STEP 5: Set permission ───────────────────────────────────
        print(f'STEP 5: Setting permission to "{request.permission}"...')
        try:
            perm_dropdown = share_frame.locator('div[role="listbox"]').first
            if perm_dropdown.count() > 0 and perm_dropdown.is_visible():
                perm_dropdown.click()
                page.wait_for_timeout(1000)
                option = share_frame.locator(f'[role="option"]:has-text("{request.permission}")').first
                if option.count() > 0:
                    option.click()
                    page.wait_for_timeout(500)
        except Exception:
            pass
        print(f"  Permission set to: {request.permission}")

        # ── STEP 6: Click Send ───────────────────────────────────────
        print("STEP 6: Sending invitation...")
        send_btn = share_frame.locator('button:has-text("Send")').first
        if send_btn.count() == 0:
            send_btn = share_frame.locator('button:has-text("Share")').first
        checkpoint("Click Send")
        send_btn.click()
        page.wait_for_timeout(2000)
        print("  Invitation sent.")

        print(f"\nSuccess! Shared with {request.email} as {request.permission}.")
        return GoogleDriveShareFileResult(success=True, error="")

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDriveShareFileResult(success=False, error=str(e))


def test_google_drive_share_file() -> None:
    print("=" * 60)
    print("  Google Drive – Share File")
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
            ensure_test_file_exists(page, "Test File For Share")
            request = GoogleDriveShareFileRequest(
                file_name="Test File For Share",
                email="cs0317b@gmail.com",
                permission="Editor",
            )
            result = google_drive_share_file(page, request)
            if result.success:
                print("\n  SUCCESS: File shared")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_drive_share_file)
