"""
Auto-generated Playwright script (Python)
Google Docs – Insert Table

Opens a document and inserts a table of the specified size
via Insert > Table > grid selector.

Generated on: 2026-04-21T23:38:46.744Z
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


def ensure_test_document_exists(page: Page, doc_name: str) -> str:
    """Create a new blank Google Doc, rename it, and return its URL."""
    page.goto("https://docs.google.com/document/create", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    title_input = page.locator('input[aria-label="Rename"]').first
    title_input.click()
    page.wait_for_timeout(500)
    title_input.press("Control+a")
    title_input.type(doc_name, delay=30)
    title_input.press("Enter")
    page.wait_for_timeout(2000)
    url = page.url
    print(f"  Created test document '{doc_name}': {url}")
    return url


@dataclass(frozen=True)
class GoogleDocsInsertTableRequest:
    document_url: str
    rows: int
    cols: int


@dataclass(frozen=True)
class GoogleDocsInsertTableResult:
    success: bool
    error: str


# Opens a Google Doc and inserts a table of the given size.
def google_docs_insert_table(
    page: Page,
    request: GoogleDocsInsertTableRequest,
) -> GoogleDocsInsertTableResult:

    try:
        # ── STEP 1: Navigate to the document ─────────────────────────
        print("STEP 1: Loading document...")
        checkpoint("Navigate to document")
        page.goto(
            request.document_url,
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(8000)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Click at end of document body ────────────────────
        print("STEP 2: Clicking document body...")
        doc_body = page.locator('.kix-appview-editor').first
        checkpoint("Click document body")
        doc_body.click()
        page.wait_for_timeout(500)
        # Press Ctrl+End to move to end
        page.keyboard.press("Control+End")
        page.wait_for_timeout(500)
        page.keyboard.press("Enter")
        page.wait_for_timeout(500)
        print("  Cursor at end of document.")

        # ── STEP 3: Open Insert menu ─────────────────────────────────
        print("STEP 3: Opening Insert menu...")
        insert_menu = page.locator('#docs-insert-menu').first
        if insert_menu.count() == 0:
            insert_menu = page.locator('div[id="docs-insert-menu"]').first
        checkpoint("Click Insert menu")
        insert_menu.click()
        page.wait_for_timeout(1500)
        print("  Insert menu opened.")

        # ── STEP 4: Hover over Table ─────────────────────────────────
        print("STEP 4: Hovering over Table...")
        # Use menu-specific selector to avoid matching document title
        table_item = page.locator('[role="menu"] span:has-text("Table")').first
        if table_item.count() == 0:
            table_item = page.locator('.goog-menuitem:has-text("Table")').first
        checkpoint("Hover Table submenu")
        table_item.hover()
        page.wait_for_timeout(1500)
        print("  Table grid visible.")

        # ── STEP 5: Select table size ────────────────────────────────
        print(f"STEP 5: Selecting {request.cols}x{request.rows} table...")
        # Google Docs uses a goog-dimension-picker with overlapping layers.
        # Use force click to bypass interception by the unhighlighted overlay.
        mousecatcher = page.locator('.goog-dimension-picker-mousecatcher').first
        checkpoint(f"Click table grid cell: {request.cols}x{request.rows}")
        cell_size = 18
        x_offset = int((request.cols - 0.5) * cell_size)
        y_offset = int((request.rows - 0.5) * cell_size)
        mousecatcher.click(position={"x": x_offset, "y": y_offset}, force=True)
        page.wait_for_timeout(2000)
        print(f"  Table {request.cols}x{request.rows} inserted.")

        print(f"\nSuccess! Inserted {request.cols}x{request.rows} table.")
        return GoogleDocsInsertTableResult(success=True, error="")

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDocsInsertTableResult(success=False, error=str(e))


def test_google_docs_insert_table() -> None:
    print("=" * 60)
    print("  Google Docs – Insert Table")
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
            doc_url = ensure_test_document_exists(page, "Test Doc For Table")
            request = GoogleDocsInsertTableRequest(
                document_url=doc_url,
                rows=2,
                cols=3,
            )
            result = google_docs_insert_table(page, request)
            if result.success:
                print("\n  SUCCESS: Table inserted")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_docs_insert_table)
