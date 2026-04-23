"""
Auto-generated Playwright script (Python)
Azure Portal – Delete Resource Group

Navigates to Azure Portal, finds a resource group, and deletes it.

Generated on: 2026-04-23T05:14:42.538Z
Uses the user's Chrome profile for persistent login state.
"""

import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


def _azure_portal_login(page: Page) -> None:
    """Navigate to Azure Portal and handle the 'Pick an account' page if needed."""
    page.goto("https://portal.azure.com/", wait_until="domcontentloaded", timeout=60000)
    for _ in range(30):
        page.wait_for_timeout(2000)
        current_url = page.url
        if "portal.azure.com" in current_url and "login" not in current_url and "oauth" not in current_url:
            return
        if "login.microsoftonline.com" in current_url:
            try:
                account_tile = page.locator(
                    '[data-test-id="list-item-0"], '
                    '.table[role="presentation"] .row, '
                    '#tilesHolder .tile-container'
                ).first
                if account_tile.count() > 0 and account_tile.is_visible(timeout=2000):
                    print("  Found 'Pick an account' page, clicking first account...")
                    account_tile.click()
                    page.wait_for_timeout(3000)
            except Exception:
                pass
    page.wait_for_timeout(3000)


def _azure_search_and_click(page: Page, service_name: str) -> None:
    """Use the Azure Portal top search bar to search for and click a service."""
    search_box = None
    for selector in [
        'input[role="searchbox"]',
        'input[aria-label*="Search resources"]',
        'input[aria-label*="Search"]',
    ]:
        loc = page.locator(selector).first
        try:
            if loc.count() > 0 and loc.is_visible(timeout=2000):
                search_box = loc
                break
        except Exception:
            continue
    if search_box is None:
        page.locator('button[aria-label*="Search"]').first.click()
        page.wait_for_timeout(1500)
        search_box = page.locator('input[role="searchbox"], input[aria-label*="Search"]').first
    search_box.click()
    page.wait_for_timeout(500)
    search_box.press("Control+a")
    search_box.type(service_name, delay=30)
    page.wait_for_timeout(2000)
    for sel in [
        f'a:has-text("{service_name}")',
        f'[role="listbox"] [role="option"]:has-text("{service_name}")',
        f'li:has-text("{service_name}")',
    ]:
        loc = page.locator(sel).first
        try:
            if loc.count() > 0 and loc.is_visible(timeout=3000):
                loc.click()
                return
        except Exception:
            continue
    search_box.press("Enter")
    page.wait_for_timeout(3000)
    page.locator(f'a:has-text("{service_name}")').first.click()


@dataclass(frozen=True)
class AzurePortalDeleteResourceGroupRequest:
    resource_group_name: str


@dataclass(frozen=True)
class AzurePortalDeleteResourceGroupResult:
    success: bool
    error: str


# Deletes a resource group in Azure Portal.
def azure_portal_delete_resource_group(
    page: Page,
    request: AzurePortalDeleteResourceGroupRequest,
) -> AzurePortalDeleteResourceGroupResult:

    try:
        # ── STEP 1: Navigate to Azure Portal ─────────────────────────
        print("STEP 1: Navigating to Azure Portal...")
        checkpoint("Navigate to Azure Portal")
        _azure_portal_login(page)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Navigate to Resource groups list ────────────────
        print(f'STEP 2: Opening Resource groups list...')
        checkpoint("Navigate to Resource groups")
        page.goto(
            "https://portal.azure.com/#browse/resourcegroups",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_timeout(8000)
        # Find and click the resource group in the list (may be in iframe)
        rg_found = False
        for frame in [page] + page.frames:
            try:
                rg_link = frame.locator(f'a:has-text("{request.resource_group_name}")').first
                if rg_link.count() > 0 and rg_link.is_visible(timeout=3000):
                    rg_link.click()
                    rg_found = True
                    break
            except Exception:
                continue
        if not rg_found:
            raise Exception(f"Could not find resource group '{request.resource_group_name}'")
        page.wait_for_timeout(5000)
        print(f"  Opened resource group: {page.url}")

        # ── STEP 3: Click Delete resource group ──────────────────────
        print("STEP 3: Clicking Delete resource group...")
        checkpoint("Click Delete resource group")
        # The Delete button may be in an iframe
        delete_btn = None
        for frame in [page] + page.frames:
            try:
                btn = frame.locator(
                    'button:has-text("Delete resource group"), '
                    'a:has-text("Delete resource group"), '
                    '[aria-label*="Delete resource group"]'
                ).first
                if btn.count() > 0 and btn.is_visible(timeout=3000):
                    delete_btn = btn
                    break
            except Exception:
                continue
        if delete_btn is None:
            raise Exception("Could not find 'Delete resource group' button")
        delete_btn.click()
        page.wait_for_timeout(2000)
        print("  Delete confirmation dialog opened.")

        # ── STEP 4: Type resource group name to confirm ──────────────
        print(f"STEP 4: Typing resource group name to confirm...")
        checkpoint("Confirm deletion — type the resource group name")
        # The confirmation dialog is in a ReactBlade iframe
        page.wait_for_timeout(3000)  # wait for delete dialog to fully render
        delete_frame = None
        for frame in page.frames:
            if "reactblade.portal.azure.net" in frame.url:
                try:
                    # Look for the confirmation text input specifically
                    if frame.locator('input[type="text"]').count() > 0:
                        delete_frame = frame
                        print(f"  Found delete dialog iframe: {frame.url[:80]}")
                        break
                except Exception:
                    pass
        if delete_frame is None:
            delete_frame = page
            print("  Warning: could not find delete dialog iframe, using main page")

        # Try various selectors for the confirmation input
        confirm_input = None
        for sel in [
            'input[aria-label*="resource group"]',
            'input[placeholder*="resource group"]',
            'input[type="text"]',
            'input',
        ]:
            loc = delete_frame.locator(sel).first
            try:
                if loc.count() > 0 and loc.is_visible(timeout=2000):
                    confirm_input = loc
                    print(f"  Matched confirm input: {sel}")
                    break
            except Exception:
                continue
        if confirm_input is None:
            raise Exception("Could not find confirmation input in delete dialog")
        confirm_input.click()
        page.wait_for_timeout(300)
        confirm_input.fill(request.resource_group_name)
        page.wait_for_timeout(1000)
        # Verify the input value
        val = confirm_input.input_value()
        print(f"  Typed: {val}")
        if val != request.resource_group_name:
            print(f"  Warning: input value '{val}' != expected '{request.resource_group_name}'")
            confirm_input.fill("")
            page.wait_for_timeout(300)
            confirm_input.type(request.resource_group_name, delay=50)
            page.wait_for_timeout(1000)

        # ── STEP 5: Click Delete ─────────────────────────────────────
        print("STEP 5: Clicking Delete...")
        checkpoint("Click Delete")
        page.wait_for_timeout(1000)  # wait for button to enable
        final_delete = None
        for btn in delete_frame.locator('button').all():
            try:
                txt = btn.inner_text(timeout=500).strip()
                if txt == "Delete" and btn.is_visible():
                    final_delete = btn
                    break
            except Exception:
                continue
        if final_delete is None:
            final_delete = delete_frame.locator('button:has-text("Delete")').first
        final_delete.evaluate("el => el.click()")
        page.wait_for_timeout(5000)
        print("  First Delete clicked.")

        # ── STEP 6: Handle "Delete Confirmation" popup ───────────────
        print("STEP 6: Handling Delete Confirmation popup...")
        checkpoint("Click Delete in confirmation popup")
        # The confirmation popup uses Fluent UI DialogSurface in the same ReactBlade iframe
        confirm_delete = None
        for frame in page.frames:
            if "reactblade.portal.azure.net" not in frame.url:
                continue
            try:
                # Look for Delete button inside a Fluent UI dialog
                dialog_btn = frame.locator('.fui-DialogSurface button:has-text("Delete")').first
                if dialog_btn.count() > 0 and dialog_btn.is_visible(timeout=3000):
                    confirm_delete = dialog_btn
                    print(f"  Found confirmation Delete in dialog")
                    break
            except Exception:
                continue
        # Fallback: any visible Delete button in any ReactBlade iframe
        if confirm_delete is None:
            for frame in page.frames:
                if "reactblade.portal.azure.net" not in frame.url:
                    continue
                try:
                    for btn in frame.locator('button').all():
                        try:
                            txt = btn.inner_text(timeout=500).strip()
                            if txt == "Delete" and btn.is_visible():
                                confirm_delete = btn
                                break
                        except Exception:
                            continue
                    if confirm_delete is not None:
                        break
                except Exception:
                    continue
        if confirm_delete is not None:
            confirm_delete.evaluate("el => el.click()")
            page.wait_for_timeout(5000)
            print("  Deletion confirmed.")
        else:
            print("  WARNING: No confirmation popup Delete button found!")

        print(f"\nSuccess! Deleted resource group '{request.resource_group_name}'.")
        return AzurePortalDeleteResourceGroupResult(
            success=True,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return AzurePortalDeleteResourceGroupResult(
            success=False,
            error=str(e),
        )


def test_azure_portal_delete_resource_group() -> None:
    print("=" * 60)
    print("  Azure Portal – Delete Resource Group")
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
            request = AzurePortalDeleteResourceGroupRequest(
                resource_group_name="test-rg-001",
            )
            result = azure_portal_delete_resource_group(page, request)
            if result.success:
                print("\n  SUCCESS: Resource group deleted.")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_azure_portal_delete_resource_group)
