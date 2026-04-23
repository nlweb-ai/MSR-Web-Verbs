"""
Auto-generated Playwright script (Python)
Google Docs – Create Document From Template

Opens the template gallery, picks a template by name, and renames
the resulting document.

Generated on: 2026-04-21T23:32:57.590Z
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
class GoogleDocsCreateFromTemplateRequest:
    template_name: str
    document_name: str


@dataclass(frozen=True)
class GoogleDocsCreateFromTemplateResult:
    success: bool
    document_url: str
    document_title: str
    error: str


# Opens the template gallery, picks a template by name, and renames the document.
def google_docs_create_from_template(
    page: Page,
    request: GoogleDocsCreateFromTemplateRequest,
) -> GoogleDocsCreateFromTemplateResult:

    try:
        # ── STEP 1: Navigate to Google Docs homepage ─────────────────
        print("STEP 1: Loading Google Docs homepage...")
        checkpoint("Navigate to Google Docs homepage")
        page.goto(
            "https://docs.google.com/",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(5000)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Expand template gallery ──────────────────────────
        print("STEP 2: Expanding template gallery...")
        gallery_btn = page.locator('[aria-label="Template gallery"]').first
        checkpoint("Click Template gallery")
        gallery_btn.click()
        page.wait_for_timeout(2000)
        print("  Template gallery expanded.")

        # ── STEP 3: Click the desired template ───────────────────────
        print(f'STEP 3: Selecting template "{request.template_name}"...')
        # Templates are card containers; find the one whose title matches
        cards = page.locator('.docs-homescreen-templates-templateview')
        card_count = cards.count()
        clicked = False
        for i in range(card_count):
            card = cards.nth(i)
            text = card.inner_text()
            if request.template_name in text and f'News{request.template_name.lower()}' not in text.lower():
                checkpoint(f"Click template: {request.template_name}")
                card.click()
                clicked = True
                break
        if not clicked:
            raise Exception(f'Template "{request.template_name}" not found among {card_count} cards')
        # Wait for the document editor to load
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(8000)
        print("  Template loaded.")

        # ── STEP 4: Rename the document ──────────────────────────────
        print(f'STEP 4: Renaming document to "{request.document_name}"...')
        title_input = page.locator('input[aria-label="Rename"]').first
        checkpoint(f"Rename document: {request.document_name}")
        title_input.click()
        page.wait_for_timeout(500)
        title_input.press("Control+a")
        title_input.type(request.document_name, delay=30)
        title_input.press("Enter")
        page.wait_for_timeout(2000)
        print("  Renamed.")

        doc_url = page.url
        print(f"\nSuccess! Document from template: {doc_url}")
        return GoogleDocsCreateFromTemplateResult(
            success=True,
            document_url=doc_url,
            document_title=request.document_name,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return GoogleDocsCreateFromTemplateResult(
            success=False, document_url="", document_title="", error=str(e),
        )


def test_google_docs_create_from_template() -> None:
    print("=" * 60)
    print("  Google Docs – Create Document From Template")
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
            request = GoogleDocsCreateFromTemplateRequest(
                template_name="Letter",
                document_name="My Letter",
            )
            result = google_docs_create_from_template(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.document_url}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_google_docs_create_from_template)
