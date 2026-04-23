"""
Auto-generated Playwright script (Python)
Google Docs – Find and Replace

Opens a document, opens Find and Replace (Ctrl+H), enters search
and replacement text, clicks Replace All, and returns the count.

Generated on: 2026-04-21T23:39:56.510Z
Recorded 6 browser interactions

Uses the user's Chrome profile for persistent login state.
"""

import os
import re
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


def ensure_test_document_exists(page: Page, doc_name: str, body_text: str = "") -> str:
    """Create a new blank Google Doc, rename it, optionally type body text, and return its URL."""
    page.goto("https://docs.google.com/document/create", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    title_input = page.locator('input[aria-label="Rename"]').first
    title_input.click()
    page.wait_for_timeout(500)
    title_input.press("Control+a")
    title_input.type(doc_name, delay=30)
    title_input.press("Enter")
    page.wait_for_timeout(2000)
    if body_text:
        doc_body = page.locator('div.kix-appview-editor').first
        doc_body.click()
        page.wait_for_timeout(500)
        page.keyboard.type(body_text, delay=20)
        page.wait_for_timeout(1000)
    url = page.url
    print(f"  Created test document '{doc_name}': {url}")
    return url


@dataclass(frozen=True)
class GoogleDocsFindAndReplaceRequest:
    document_url: str
    find_text: str
    replace_text: str


@dataclass(frozen=True)
class GoogleDocsFindAndReplaceResult:
    success: bool
    replacements_count: int
    error: str


# Opens a Google Doc and performs Find and Replace.
def google_docs_find_and_replace(
    page: Page,
    request: GoogleDocsFindAndReplaceRequest,
) -> GoogleDocsFindAndReplaceResult:

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

        # ── STEP 2: Open Find and Replace (Ctrl+H) ──────────────────
        print("STEP 2: Opening Find and Replace...")
        checkpoint("Open Find and Replace (Ctrl+H)")
        page.keyboard.press("Control+h")
        page.wait_for_timeout(2000)
        print("  Dialog opened.")

        # ── STEP 3: Enter find text ──────────────────────────────────
        print(f'STEP 3: Entering find text "{request.find_text}"...')
        find_input = page.locator('input[aria-label="Find"]').first
        if find_input.count() == 0:
            find_input = page.locator('[aria-label="Find in document"] input').first
        checkpoint(f"Type find text: {request.find_text}")
        find_input.click()
        find_input.press("Control+a")
        find_input.type(request.find_text, delay=30)
        page.wait_for_timeout(1000)
        print("  Find text entered.")

        # ── STEP 4: Enter replace text ───────────────────────────────
        print(f'STEP 4: Entering replace text "{request.replace_text}"...')
        replace_input = page.locator('input[aria-label="Replace with"]').first
        if replace_input.count() == 0:
            replace_input = page.locator('[aria-label="Replace with"] input').first
        checkpoint(f"Type replace text: {request.replace_text}")
        replace_input.click()
        replace_input.press("Control+a")
        replace_input.type(request.replace_text, delay=30)
        page.wait_for_timeout(1000)
        print("  Replace text entered.")

        # ── STEP 5: Click Replace All ────────────────────────────────
        print("STEP 5: Clicking Replace All...")
        replace_all_btn = page.locator('button:has-text("Replace all")').first
        if replace_all_btn.count() == 0:
            replace_all_btn = page.locator('[aria-label="Replace all"]').first
        checkpoint("Click Replace All")
        replace_all_btn.click()
        page.wait_for_timeout(2000)

        # Try to read the replacement count from the status
        status_text = ""
        status_el = page.locator('.docs-findinput-count').first
        if status_el.count() > 0:
            status_text = status_el.text_content() or ""
        count = 0
        match = re.search(r"(\d+)", status_text)
        if match:
            count = int(match.group(1))
        print(f"  Replacements: {count}")

        # ── STEP 6: Close dialog ─────────────────────────────────────
        print("STEP 6: Closing Find and Replace dialog...")
        checkpoint("Close Find and Replace dialog")
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        print("  Dialog closed.")

        print(f"\nSuccess! Replaced {count} occurrences.")
        return GoogleDocsFindAndReplaceResult(
            success=True, replacements_count=count, error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDocsFindAndReplaceResult(
            success=False, replacements_count=0, error=str(e),
        )


def test_google_docs_find_and_replace() -> None:
    print("=" * 60)
    print("  Google Docs – Find and Replace")
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
            doc_url = ensure_test_document_exists(page, "Test Doc For FindReplace", body_text="hello world hello again hello")
            request = GoogleDocsFindAndReplaceRequest(
                document_url=doc_url,
                find_text="hello",
                replace_text="world",
            )
            result = google_docs_find_and_replace(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.replacements_count} replacements")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_docs_find_and_replace)
