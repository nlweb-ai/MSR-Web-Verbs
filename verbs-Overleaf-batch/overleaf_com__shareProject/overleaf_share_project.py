"""
Playwright script (Python) — Overleaf Share Project

Shares an Overleaf project with a collaborator by email, assigning a role
(Editor, Viewer, or Reviewer).

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
class OverleafShareProjectRequest:
    project_id: str
    collaborator_email: str
    role: str  # "Editor", "Viewer", or "Reviewer"


@dataclass(frozen=True)
class OverleafShareProjectResult:
    success: bool
    error: str


# Shares an Overleaf project with a collaborator by opening the project editor,
# clicking the Share button, selecting the collaborator role from the dropdown,
# entering the collaborator's email, and clicking Invite.
def share_overleaf_project(
    page: Page,
    request: OverleafShareProjectRequest,
) -> OverleafShareProjectResult:
    project_url = f"https://www.overleaf.com/project/{request.project_id}"

    try:
        # ── STEP 1: Navigate to project ───────────────────────────────
        print(f"STEP 1: Navigating to project {request.project_id}...")
        checkpoint("Navigate to project")
        page.goto(project_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(5000)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Click Share button ────────────────────────────────
        print("STEP 2: Clicking Share button...")
        share_btn = page.locator('button:has-text("Share")')
        share_btn.wait_for(state="visible", timeout=10000)
        checkpoint("Click Share button")
        share_btn.click()
        page.wait_for_timeout(2000)
        print("  Share dialog opened")

        # ── STEP 3: Select role ───────────────────────────────────────
        print(f"STEP 3: Selecting role '{request.role}'...")
        role_input = page.locator('[data-testid="add-collaborator-select"]')
        current_role = role_input.input_value()
        if current_role != request.role:
            checkpoint(f"Open role dropdown")
            role_input.click()
            page.wait_for_timeout(1000)
            role_option = page.locator(
                f'button[role="option"]:has-text("{request.role}")'
            ).first
            checkpoint(f"Select role: {request.role}")
            role_option.click()
            page.wait_for_timeout(500)
            print(f"  Selected role: {request.role}")
        else:
            print(f"  Role already set to: {request.role}")

        # ── STEP 4: Enter collaborator email ──────────────────────────
        print(f"STEP 4: Entering email '{request.collaborator_email}'...")
        email_input = page.locator('[data-testid="collaborator-email-input"]')
        checkpoint("Click email input")
        email_input.click()
        page.wait_for_timeout(500)
        email_input.press("Control+a")
        checkpoint(f"Type email: {request.collaborator_email}")
        email_input.fill(request.collaborator_email)
        page.wait_for_timeout(1000)
        print(f"  Entered email: {request.collaborator_email}")

        # ── STEP 5: Click Invite ──────────────────────────────────────
        print("STEP 5: Clicking Invite button...")
        invite_btn = page.locator('[role="dialog"] button:has-text("Invite")')
        checkpoint("Click Invite button")
        invite_btn.click()
        page.wait_for_timeout(2000)
        print("  Invite sent!")

        # ── STEP 6: Verify and close ──────────────────────────────────
        print("STEP 6: Verifying invitation...")
        dialog = page.locator('[role="dialog"]')
        dialog_text = dialog.inner_text(timeout=3000)
        if request.collaborator_email in dialog_text:
            print(f"  Confirmed: {request.collaborator_email} added as {request.role}")
        else:
            print("  Note: Could not confirm invitation in dialog text")

        close_btn = page.locator('[role="dialog"] button:has-text("Close")')
        checkpoint("Close share dialog")
        close_btn.click()
        page.wait_for_timeout(1000)
        print("  Dialog closed")

        return OverleafShareProjectResult(success=True, error="")

    except Exception as e:
        print(f"ERROR: {e}")
        return OverleafShareProjectResult(success=False, error=str(e))


def test_share_overleaf_project() -> None:
    request = OverleafShareProjectRequest(
        project_id="69e6b0a3d05bcdbdf251587c",
        collaborator_email="shuochen@live.com",
        role="Editor",
    )

    print("=" * 60)
    print("  Overleaf – Share Project")
    print(f"  Project: {request.project_id}")
    print(f"  Invite: {request.collaborator_email} as {request.role}")
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
            result = share_overleaf_project(page, request)
            assert result.success, f"Share failed: {result.error}"
            print(f"\n  SUCCESS: Project shared with {request.collaborator_email} as {request.role}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_share_overleaf_project)
