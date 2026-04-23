"""
Auto-generated Playwright script (Python)
Google Docs – Share Document

Opens a document, clicks Share, enters an email and permission,
and sends the invitation.

Generated on: 2026-04-21T23:35:23.957Z
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
class GoogleDocsShareDocumentRequest:
    document_url: str
    email: str
    permission: str  # "Editor", "Viewer", or "Commenter"


@dataclass(frozen=True)
class GoogleDocsShareDocumentResult:
    success: bool
    error: str


# Opens a Google Doc and shares it with the given email and permission.
def google_docs_share_document(
    page: Page,
    request: GoogleDocsShareDocumentRequest,
) -> GoogleDocsShareDocumentResult:

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

        # ── STEP 2: Click the Share button ───────────────────────────
        print("STEP 2: Opening Share dialog...")
        share_btn = page.locator('div[aria-label*="Share. "]').first
        checkpoint("Click Share button")
        share_btn.click()
        page.wait_for_timeout(4000)
        print("  Share dialog opened.")

        # The share dialog lives inside a drivesharing iframe
        share_frame = page.frame_locator('iframe[src*="drivesharing"]')

        # ── STEP 3: Enter email address ──────────────────────────────
        print(f'STEP 3: Entering email "{request.email}"...')
        email_input = share_frame.locator(
            'input[aria-label="Add people, groups, spaces, and calendar events"]'
        ).first
        checkpoint(f"Type email: {request.email}")
        email_input.click()
        email_input.type(request.email, delay=30)
        page.wait_for_timeout(1500)
        page.keyboard.press("Enter")
        page.wait_for_timeout(2000)
        print("  Email entered.")

        # ── STEP 4: Set permission ───────────────────────────────────
        print(f'STEP 4: Setting permission to "{request.permission}"...')
        # After adding a person, a role dropdown may appear (default is Editor)
        # The dropdown is a button with role text like "Editor", "Viewer", etc.
        try:
            role_dropdown = share_frame.locator(
                'div[role="listbox"], div[aria-haspopup="listbox"]'
            ).first
            if role_dropdown.count() > 0 and role_dropdown.is_visible():
                checkpoint(f"Set permission: {request.permission}")
                role_dropdown.click()
                page.wait_for_timeout(500)
                role_option = share_frame.locator(
                    f'[role="option"]:has-text("{request.permission}")'
                ).first
                if role_option.count() > 0:
                    role_option.click()
                    page.wait_for_timeout(500)
        except Exception:
            pass  # Default permission (Editor) is acceptable
        print(f"  Permission set to: {request.permission}")

        # ── STEP 5: Click Send ───────────────────────────────────────
        print("STEP 5: Sending invitation...")
        send_btn = share_frame.locator('button:has-text("Send")').first
        if send_btn.count() == 0:
            send_btn = share_frame.locator('button:has-text("Done")').first
        checkpoint("Click Send")
        send_btn.click()
        page.wait_for_timeout(2000)
        print("  Invitation sent.")

        print(f"\nSuccess! Shared with {request.email} as {request.permission}.")
        return GoogleDocsShareDocumentResult(success=True, error="")

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDocsShareDocumentResult(success=False, error=str(e))


def test_google_docs_share_document() -> None:
    print("=" * 60)
    print("  Google Docs – Share Document")
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
            doc_url = ensure_test_document_exists(page, "Test Doc For Sharing")
            request = GoogleDocsShareDocumentRequest(
                document_url=doc_url,
                email="cs0317b@gmail.com",
                permission="Editor",
            )
            result = google_docs_share_document(page, request)
            if result.success:
                print("\n  SUCCESS: Document shared")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_docs_share_document)
