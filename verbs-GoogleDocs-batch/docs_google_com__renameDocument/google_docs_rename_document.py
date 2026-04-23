"""
Auto-generated Playwright script (Python)
Google Docs – Rename Document

Opens a document by URL and renames it via the title input.

Generated on: 2026-04-21T23:34:05.976Z
Recorded 2 browser interactions

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
class GoogleDocsRenameDocumentRequest:
    document_url: str
    new_name: str


@dataclass(frozen=True)
class GoogleDocsRenameDocumentResult:
    success: bool
    new_title: str
    error: str


# Opens a Google Doc by URL and renames it.
def google_docs_rename_document(
    page: Page,
    request: GoogleDocsRenameDocumentRequest,
) -> GoogleDocsRenameDocumentResult:

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

        # ── STEP 2: Rename the document ──────────────────────────────
        print(f'STEP 2: Renaming to "{request.new_name}"...')
        title_input = page.locator('input[aria-label="Rename"]').first
        checkpoint(f"Rename document: {request.new_name}")
        title_input.click()
        page.wait_for_timeout(500)
        title_input.press("Control+a")
        title_input.type(request.new_name, delay=30)
        title_input.press("Enter")
        page.wait_for_timeout(2000)
        print(f"  Renamed to: {request.new_name}")

        print(f"\nSuccess! Document renamed to \"{request.new_name}\".")
        return GoogleDocsRenameDocumentResult(
            success=True, new_title=request.new_name, error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDocsRenameDocumentResult(
            success=False, new_title="", error=str(e),
        )


def test_google_docs_rename_document() -> None:
    print("=" * 60)
    print("  Google Docs – Rename Document")
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
            doc_url = ensure_test_document_exists(page, "Test Doc For Rename")
            request = GoogleDocsRenameDocumentRequest(
                document_url=doc_url,
                new_name="Renamed Document",
            )
            result = google_docs_rename_document(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.new_title}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_docs_rename_document)
