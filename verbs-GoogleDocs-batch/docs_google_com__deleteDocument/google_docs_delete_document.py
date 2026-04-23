"""
Auto-generated Playwright script (Python)
Google Docs – Delete Document

Opens a document and moves it to trash via File > Move to trash.

Generated on: 2026-04-21T23:36:34.290Z
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
class GoogleDocsDeleteDocumentRequest:
    document_url: str


@dataclass(frozen=True)
class GoogleDocsDeleteDocumentResult:
    success: bool
    error: str


# Opens a Google Doc and moves it to trash.
def google_docs_delete_document(
    page: Page,
    request: GoogleDocsDeleteDocumentRequest,
) -> GoogleDocsDeleteDocumentResult:

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

        # ── STEP 2: Open File menu ───────────────────────────────────
        print("STEP 2: Opening File menu...")
        file_menu = page.locator('#docs-file-menu').first
        if file_menu.count() == 0:
            file_menu = page.locator('div[id="docs-file-menu"]').first
        checkpoint("Click File menu")
        file_menu.click()
        page.wait_for_timeout(1500)
        print("  File menu opened.")

        # ── STEP 3: Click "Move to trash" ────────────────────────────
        print("STEP 3: Clicking Move to trash...")
        trash_item = page.locator('span:has-text("Move to trash")').first
        if trash_item.count() == 0:
            trash_item = page.locator('[aria-label*="Move to trash"]').first
        checkpoint("Click Move to trash")
        trash_item.click()
        page.wait_for_timeout(2000)
        print("  Document moved to trash.")

        print("\nSuccess! Document moved to trash.")
        return GoogleDocsDeleteDocumentResult(success=True, error="")

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDocsDeleteDocumentResult(success=False, error=str(e))


def test_google_docs_delete_document() -> None:
    print("=" * 60)
    print("  Google Docs – Delete Document")
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
            doc_url = ensure_test_document_exists(page, "Test Doc For Deletion")
            request = GoogleDocsDeleteDocumentRequest(
                document_url=doc_url,
            )
            result = google_docs_delete_document(page, request)
            if result.success:
                print("\n  SUCCESS: Document moved to trash")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_docs_delete_document)
