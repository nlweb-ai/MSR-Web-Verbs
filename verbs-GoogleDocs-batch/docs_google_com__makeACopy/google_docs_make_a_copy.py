"""
Auto-generated Playwright script (Python)
Google Docs – Make a Copy

Opens a document, uses File > Make a copy, confirms the dialog,
and returns the new document URL.

Generated on: 2026-04-21T23:37:58.677Z
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
class GoogleDocsMakeACopyRequest:
    document_url: str
    copy_name: str


@dataclass(frozen=True)
class GoogleDocsMakeACopyResult:
    success: bool
    new_document_url: str
    new_document_title: str
    error: str


# Opens a Google Doc and makes a copy via File > Make a copy.
def google_docs_make_a_copy(
    page: Page,
    request: GoogleDocsMakeACopyRequest,
) -> GoogleDocsMakeACopyResult:

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

        # ── STEP 3: Click "Make a copy" ──────────────────────────────
        print("STEP 3: Clicking Make a copy...")
        copy_item = page.locator('span:has-text("Make a copy")').first
        if copy_item.count() == 0:
            copy_item = page.locator('[aria-label*="Make a copy"]').first
        checkpoint("Click Make a copy")
        copy_item.click()
        page.wait_for_timeout(2000)
        print("  Copy dialog opened.")

        # ── STEP 4: Set the copy name ────────────────────────────────
        print(f'STEP 4: Setting copy name to "{request.copy_name}"...')
        name_input = page.locator('input[type="text"]').first
        checkpoint(f"Type copy name: {request.copy_name}")
        name_input.press("Control+a")
        name_input.type(request.copy_name, delay=30)
        page.wait_for_timeout(500)
        print("  Name set.")

        # ── STEP 5: Confirm the copy ─────────────────────────────────
        print("STEP 5: Confirming copy...")
        context = page.context
        with context.expect_page(timeout=15000) as new_page_info:
            ok_btn = page.locator('button:has-text("Make a copy")').first
            if ok_btn.count() == 0:
                ok_btn = page.locator('button:has-text("OK")').first
            checkpoint("Click Make a copy / OK")
            ok_btn.click()
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded")
        new_page.wait_for_timeout(5000)
        new_url = new_page.url
        print(f"  Copy created: {new_url}")

        print(f"\nSuccess! Copy at {new_url}")
        return GoogleDocsMakeACopyResult(
            success=True,
            new_document_url=new_url,
            new_document_title=request.copy_name,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDocsMakeACopyResult(
            success=False, new_document_url="", new_document_title="", error=str(e),
        )


def test_google_docs_make_a_copy() -> None:
    print("=" * 60)
    print("  Google Docs – Make a Copy")
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
            doc_url = ensure_test_document_exists(page, "Test Doc For Copy")
            request = GoogleDocsMakeACopyRequest(
                document_url=doc_url,
                copy_name="Copy of Test Document 1",
            )
            result = google_docs_make_a_copy(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.new_document_url}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_docs_make_a_copy)
