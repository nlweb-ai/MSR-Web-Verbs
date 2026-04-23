"""
Auto-generated Playwright script (Python)
Google Docs – Create Document

Creates a new blank Google Doc, renames it, and types sample text.

Generated on: 2026-04-21T23:32:20.434Z
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


@dataclass(frozen=True)
class GoogleDocsCreateDocumentRequest:
    document_name: str
    sample_text: str


@dataclass(frozen=True)
class GoogleDocsCreateDocumentResult:
    success: bool
    document_url: str
    document_title: str
    error: str


# Creates a new blank Google Doc, renames it, and types sample text.
def google_docs_create_document(
    page: Page,
    request: GoogleDocsCreateDocumentRequest,
) -> GoogleDocsCreateDocumentResult:

    try:
        # ── STEP 1: Navigate to create new document ──────────────────
        print("STEP 1: Creating new Google Doc...")
        checkpoint("Navigate to create new document")
        page.goto(
            "https://docs.google.com/document/create",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(8000)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Rename the document ──────────────────────────────
        print(f'STEP 2: Renaming document to "{request.document_name}"...')
        title_input = page.locator('input[aria-label="Rename"]').first
        checkpoint(f"Rename document: {request.document_name}")
        title_input.click()
        page.wait_for_timeout(500)
        title_input.press("Control+a")
        title_input.type(request.document_name, delay=30)
        title_input.press("Enter")
        page.wait_for_timeout(2000)
        print("  Renamed.")

        # ── STEP 3: Type sample text ─────────────────────────────────
        print("STEP 3: Typing sample text...")
        # Click on the document body to focus
        doc_body = page.locator('.kix-appview-editor').first
        checkpoint("Click document body")
        doc_body.click()
        page.wait_for_timeout(500)
        checkpoint(f"Type sample text")
        page.keyboard.type(request.sample_text, delay=20)
        page.wait_for_timeout(2000)
        print("  Text typed.")

        doc_url = page.url
        print(f"\nSuccess! Document created: {doc_url}")
        return GoogleDocsCreateDocumentResult(
            success=True,
            document_url=doc_url,
            document_title=request.document_name,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDocsCreateDocumentResult(
            success=False, document_url="", document_title="", error=str(e),
        )


def test_google_docs_create_document() -> None:
    print("=" * 60)
    print("  Google Docs – Create Document")
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
            request = GoogleDocsCreateDocumentRequest(
                document_name="Test Document 1",
                sample_text="Hello, this is a test document.",
            )
            result = google_docs_create_document(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.document_url}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_docs_create_document)
