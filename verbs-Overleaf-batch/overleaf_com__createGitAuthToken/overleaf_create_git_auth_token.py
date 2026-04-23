"""
Auto-generated Playwright script (Python)
Overleaf – Create Git Authentication Token

Navigates to the Overleaf account settings page, generates a new Git
authentication token, captures it from the dialog, and closes the dialog.

Generated on: 2026-04-21T17:47:31.079Z
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


@dataclass(frozen=True)
class OverleafCreateGitAuthTokenResult:
    success: bool
    token: str
    error: str


# Navigates to the Overleaf account settings page, generates a new
# Git authentication token, retrieves the token string from the popup
# dialog, and closes the dialog.
def overleaf_create_git_auth_token(
    page: Page,
) -> OverleafCreateGitAuthTokenResult:

    try:
        # ── STEP 1: Navigate to Overleaf account settings ────────────
        print("STEP 1: Loading Overleaf account settings page...")
        checkpoint("Navigate to account settings")
        page.goto(
            "https://www.overleaf.com/user/settings",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(2000)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Scroll to Git authentication tokens section ──────
        print("STEP 2: Locating Git authentication tokens section...")
        git_heading = page.locator('h4:has-text("Your Git authentication tokens")')
        git_heading.scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        checkpoint("Found Git authentication tokens section")
        print("  Found section.")

        # ── STEP 3: Click Generate token / Add another token ─────────
        print("STEP 3: Clicking token generation button...")
        # Two possible states:
        #   (a) No tokens yet → button#generate-token-button "Generate token"
        #   (b) Tokens exist  → button.btn-inline-link "Add another token"
        gen_btn = page.locator('button#generate-token-button')
        add_btn = page.locator('button:has-text("Add another token")')

        if gen_btn.count() > 0 and gen_btn.is_visible():
            checkpoint("Click Generate token button")
            gen_btn.click()
            print('  Clicked "Generate token".')
        elif add_btn.count() > 0 and add_btn.is_visible():
            checkpoint("Click Add another token button")
            add_btn.click()
            print('  Clicked "Add another token".')
        else:
            return OverleafCreateGitAuthTokenResult(
                success=False,
                token="",
                error="Could not find Generate token or Add another token button",
            )
        page.wait_for_timeout(2000)

        # ── STEP 4: Extract token from dialog ────────────────────────
        print("STEP 4: Extracting token from dialog...")
        dialog = page.locator('[role="dialog"]')
        dialog.wait_for(state="visible", timeout=10000)

        # The token is inside: span[aria-label="Git authentication token"] > code
        token_code = dialog.locator(
            'span[aria-label="Git authentication token"] code'
        )
        token_code.wait_for(state="visible", timeout=5000)
        token = token_code.inner_text(timeout=3000).strip()
        checkpoint(f"Token retrieved: {token[:8]}...")
        print(f"  Token: {token}")

        # ── STEP 5: Close the dialog ─────────────────────────────────
        print("STEP 5: Closing dialog...")
        close_btn = dialog.locator('.modal-footer button:has-text("Close")')
        checkpoint("Click Close button")
        close_btn.click()
        page.wait_for_timeout(1000)
        print("  Dialog closed.")

        print(f"\nSuccess! Token generated: {token[:8]}...")
        return OverleafCreateGitAuthTokenResult(
            success=True,
            token=token,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return OverleafCreateGitAuthTokenResult(
            success=False,
            token="",
            error=str(e),
        )


def test_overleaf_create_git_auth_token() -> None:
    print("=" * 60)
    print("  Overleaf – Create Git Authentication Token")
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
            result = overleaf_create_git_auth_token(page)
            if result.success:
                print(f"\n  SUCCESS: Token = {result.token}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_overleaf_create_git_auth_token)
