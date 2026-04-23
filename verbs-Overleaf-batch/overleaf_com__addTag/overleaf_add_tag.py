"""
Auto-generated Playwright script (Python)
Overleaf – Add Tag

Creates a new tag on the Overleaf dashboard.

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
class OverleafAddTagRequest:
    tag_name: str


@dataclass(frozen=True)
class OverleafAddTagResult:
    success: bool
    error: str


# Creates a new tag on the Overleaf dashboard.
def overleaf_add_tag(
    page: Page,
    request: OverleafAddTagRequest,
) -> OverleafAddTagResult:

    try:
        # ── STEP 1: Navigate to project dashboard ────────────────────
        print("STEP 1: Loading Overleaf project dashboard...")
        checkpoint("Navigate to project dashboard")
        page.goto(
            "https://www.overleaf.com/project",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(2000)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Click "New Tag" in the sidebar ───────────────────
        print(f'STEP 2: Creating tag "{request.tag_name}"...')
        new_tag_btn = page.locator('button:has-text("New Tag")').first
        if new_tag_btn.count() == 0:
            new_tag_btn = page.locator('a:has-text("New Tag")').first
        checkpoint("Click New Tag button")
        new_tag_btn.click()
        page.wait_for_timeout(1000)

        # Enter tag name in the input that appears
        tag_input = page.locator('input[placeholder="Tag Name"]').first
        if tag_input.count() == 0:
            tag_input = page.locator(
                'input[name="new-tag-form-name"]'
            ).first
        if tag_input.count() == 0:
            tag_input = page.locator(
                '[role="dialog"] input[type="text"]'
            ).first
        checkpoint(f"Type tag name: {request.tag_name}")
        tag_input.type(request.tag_name, delay=30)
        page.wait_for_timeout(500)

        # Confirm tag creation
        create_btn = page.locator('button:has-text("Create")').first
        checkpoint("Click Create tag")
        create_btn.click()
        page.wait_for_timeout(2000)
        print(f"  Tag created: {request.tag_name}")

        print(f"\nSuccess! Tag \"{request.tag_name}\" created.")
        return OverleafAddTagResult(success=True, error="")

    except Exception as e:
        print(f"Error: {e}")
        return OverleafAddTagResult(success=False, error=str(e))


def test_overleaf_add_tag() -> None:
    print("=" * 60)
    print("  Overleaf – Add Tag")
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
            request = OverleafAddTagRequest(
                tag_name="test-tag",
            )
            result = overleaf_add_tag(page, request)
            if result.success:
                print("\n  SUCCESS: Tag created")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_overleaf_add_tag)
