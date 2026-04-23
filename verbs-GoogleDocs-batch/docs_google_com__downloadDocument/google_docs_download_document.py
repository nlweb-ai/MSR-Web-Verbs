"""
Auto-generated Playwright script (Python)
Google Docs – Download Document

Opens a document and downloads it via File > Download in the
desired format.

Generated on: 2026-04-21T23:36:00.842Z
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
class GoogleDocsDownloadDocumentRequest:
    document_url: str
    format: str  # e.g. "PDF Document (.pdf)", "Microsoft Word (.docx)"


@dataclass(frozen=True)
class GoogleDocsDownloadDocumentResult:
    success: bool
    downloaded_file: str
    error: str


# Opens a Google Doc and downloads it in the specified format.
def google_docs_download_document(
    page: Page,
    request: GoogleDocsDownloadDocumentRequest,
) -> GoogleDocsDownloadDocumentResult:

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

        # ── STEP 3: Hover over Download ──────────────────────────────
        print("STEP 3: Hovering over Download...")
        download_item = page.locator('[aria-label*="Download"]').first
        if download_item.count() == 0:
            download_item = page.locator('span:has-text("Download")').first
        checkpoint("Hover Download submenu")
        download_item.hover()
        page.wait_for_timeout(1500)
        print("  Download submenu opened.")

        # ── STEP 4: Click desired format ─────────────────────────────
        print(f'STEP 4: Clicking format "{request.format}"...')
        # Start download listener before clicking
        with page.expect_download(timeout=15000) as download_info:
            format_item = page.locator(f'span:has-text("{request.format}")').first
            if format_item.count() == 0:
                format_item = page.locator(f'[aria-label*="{request.format}"]').first
            checkpoint(f"Click format: {request.format}")
            format_item.click()
        download = download_info.value
        downloaded_path = download.path()
        suggested = download.suggested_filename
        page.wait_for_timeout(2000)
        print(f"  Downloaded: {suggested}")

        print(f"\nSuccess! Downloaded as {suggested}")
        return GoogleDocsDownloadDocumentResult(
            success=True, downloaded_file=suggested, error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDocsDownloadDocumentResult(
            success=False, downloaded_file="", error=str(e),
        )


def test_google_docs_download_document() -> None:
    print("=" * 60)
    print("  Google Docs – Download Document")
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
            doc_url = ensure_test_document_exists(page, "Test Doc For Download")
            request = GoogleDocsDownloadDocumentRequest(
                document_url=doc_url,
                format="PDF Document (.pdf)",
            )
            result = google_docs_download_document(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.downloaded_file}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_docs_download_document)
