"""
Auto-generated Playwright script (Python)
Google Drive – Search Files

Searches for files in Google Drive using the search bar and extracts results.

Generated on: 2026-04-22T16:34:15.207Z
Recorded 3 browser interactions

Uses the user's Chrome profile for persistent login state.
"""

import os
from dataclasses import dataclass
from typing import List
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GoogleDriveSearchFilesRequest:
    query: str
    max_results: int = 10


@dataclass(frozen=True)
class SearchFileEntry:
    name: str
    url: str


@dataclass(frozen=True)
class GoogleDriveSearchFilesResult:
    success: bool
    files: List[SearchFileEntry]
    error: str


# Searches for files in Google Drive.
def google_drive_search_files(
    page: Page,
    request: GoogleDriveSearchFilesRequest,
) -> GoogleDriveSearchFilesResult:

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

        # ── STEP 2: Click search bar and type query ──────────────────
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

        # ── STEP 3: Extract file names and URLs from results ────────
        print("STEP 3: Extracting results...")
        checkpoint("Extract search results")
        # Drive uses div[data-tooltip] for file names in the list.
        # Each file row has a parent/ancestor with data-id (the file ID).
        items = page.locator('div[data-tooltip]')
        files: list[SearchFileEntry] = []
        seen_names: set[str] = set()
        count = items.count()
        for i in range(count):
            el = items.nth(i)
            if not el.is_visible():
                continue
            tooltip = el.get_attribute("data-tooltip") or ""
            if not tooltip or len(tooltip) < 5:
                continue
            skip_keywords = [
                "Support", "Settings", "View details", "Clear selection",
                "Share (", "Download", "Move (", "Remove (", "Copy links",
                "Ready for offline", "Sort", "Layout", "Storage",
            ]
            if any(tooltip.startswith(kw) for kw in skip_keywords):
                continue
            if tooltip in seen_names:
                continue
            seen_names.add(tooltip)

            # Extract file ID from closest ancestor with data-id
            file_id = el.evaluate(
                """el => {
                    let node = el;
                    while (node && node !== document.body) {
                        if (node.dataset && node.dataset.id) return node.dataset.id;
                        node = node.parentElement;
                    }
                    return '';
                }"""
            )
            if file_id:
                url = f"https://drive.google.com/file/d/{file_id}"
            else:
                url = ""
            files.append(SearchFileEntry(name=tooltip, url=url))
            if len(files) >= request.max_results:
                break
        print(f"  Found {len(files)} results.")
        for f in files:
            print(f"    - {f.name}")
            if f.url:
                print(f"      {f.url}")

        print(f"\nSuccess! Found {len(files)} files.")
        return GoogleDriveSearchFilesResult(
            success=True,
            files=files,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDriveSearchFilesResult(
            success=False, file_names=[], error=str(e),
        )


def test_google_drive_search_files() -> None:
    print("=" * 60)
    print("  Google Drive – Search Files")
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
            request = GoogleDriveSearchFilesRequest(
                query="Test",
                max_results=10,
            )
            result = google_drive_search_files(page, request)
            if result.success and result.files:
                print(f"\n  SUCCESS: {len(result.files)} files found")
                for f in result.files:
                    print(f"    {f.name}  →  {f.url}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_drive_search_files)
