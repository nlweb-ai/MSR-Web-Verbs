"""
Auto-generated Playwright script (Python)
Google Drive – Open File

Searches for a file in Google Drive and opens the first matching result.

Generated on: 2026-04-22T16:34:18.869Z
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
class GoogleDriveOpenFileRequest:
    query: str


@dataclass(frozen=True)
class GoogleDriveOpenFileResult:
    success: bool
    file_name: str
    file_url: str
    error: str


# Searches for a file in Google Drive and opens the first match.
def google_drive_open_file(
    page: Page,
    request: GoogleDriveOpenFileRequest,
) -> GoogleDriveOpenFileResult:

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

        # ── STEP 2: Search for the file ──────────────────────────────
        print(f'STEP 2: Searching for "{request.query}"...')
        search_input = page.locator('input[aria-label="Search in Drive"]').first
        if search_input.count() == 0:
            search_input = page.locator('[role="search"] input').first
        if search_input.count() == 0:
            search_input = page.locator('input[placeholder*="Search"]').first
        checkpoint(f"Search for: {request.query}")
        search_input.click()
        page.wait_for_timeout(500)
        search_input.press("Control+a")
        search_input.type(request.query, delay=30)
        page.wait_for_timeout(500)
        search_input.press("Enter")
        page.wait_for_timeout(5000)
        print("  Search results loaded.")

        # ── STEP 3: Double-click first result ────────────────────────
        print("STEP 3: Opening first result...")
        # After search, results appear as div[data-tooltip] with the file name
        candidates = page.locator('div[data-tooltip]')

        # Try to find a visible file item to double-click
        first_item = None
        file_name = "Unknown"

        # Strategy 1: data-tooltip items containing the search query
        for i in range(candidates.count()):
            c = candidates.nth(i)
            if not c.is_visible():
                continue
            tooltip = c.get_attribute("data-tooltip") or ""
            if tooltip and len(tooltip) > 3 and request.query.lower() in tooltip.lower():
                first_item = c
                file_name = tooltip
                break

        # Strategy 2: any visible data-tooltip item that isn't a toolbar button
        if first_item is None:
            for i in range(candidates.count()):
                c = candidates.nth(i)
                if not c.is_visible():
                    continue
                tooltip = c.get_attribute("data-tooltip") or ""
                if tooltip and len(tooltip) > 10:
                    first_item = c
                    file_name = tooltip
                    break

        if first_item is None:
            raise Exception("No file items found in search results")

        print(f"  Selected: '{file_name}'")
        checkpoint(f"Double-click file: {file_name}")
        first_item.dblclick()
        page.wait_for_timeout(5000)
        print(f"  Opened: {file_name}")

        # ── STEP 4: Get the file URL ─────────────────────────────────
        print("STEP 4: Getting file URL...")
        # Check if a new tab opened
        pages = page.context.pages
        if len(pages) > 1:
            new_page = pages[-1]
            file_url = new_page.url
        else:
            file_url = page.url
        print(f"  URL: {file_url}")

        print(f"\nSuccess! Opened '{file_name}' at {file_url}")
        return GoogleDriveOpenFileResult(
            success=True,
            file_name=file_name,
            file_url=file_url,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDriveOpenFileResult(
            success=False, file_name="", file_url="", error=str(e),
        )


def test_google_drive_open_file() -> None:
    print("=" * 60)
    print("  Google Drive – Open File")
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
            request = GoogleDriveOpenFileRequest(
                query="Test",
            )
            result = google_drive_open_file(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.file_name} at {result.file_url}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_drive_open_file)
