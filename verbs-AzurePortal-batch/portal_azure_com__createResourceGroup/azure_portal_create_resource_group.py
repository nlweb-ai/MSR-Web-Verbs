"""
Auto-generated Playwright script (Python)
Azure Portal – Create Resource Group

Navigates to Azure Portal, opens Resource Groups, and creates a new one.

Generated on: 2026-04-23T04:59:18.770Z
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
    # Click the matching result
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
    # Fallback: press Enter
    search_box.press("Enter")
    page.wait_for_timeout(3000)
    page.locator(f'a:has-text("{service_name}")').first.click()


@dataclass(frozen=True)
class AzurePortalCreateResourceGroupRequest:
    resource_group_name: str
    region: str


@dataclass(frozen=True)
class AzurePortalCreateResourceGroupResult:
    success: bool
    resource_group_name: str
    error: str


# Creates a new resource group in Azure Portal.
def azure_portal_create_resource_group(
    page: Page,
    request: AzurePortalCreateResourceGroupRequest,
) -> AzurePortalCreateResourceGroupResult:

    try:
        # ── STEP 1: Navigate to Azure Portal ─────────────────────────
        print("STEP 1: Navigating to Azure Portal...")
        checkpoint("Navigate to Azure Portal")
        _azure_portal_login(page)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Navigate to Create Resource Group form ─────────
        print("STEP 2: Opening Create Resource Group form...")
        checkpoint("Navigate to Create Resource Group form")
        page.goto(
            "https://portal.azure.com/#create/Microsoft.ResourceGroup",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_timeout(10000)
        print(f"  Loaded: {page.url}")

        # The form lives inside a ReactBlade iframe
        form_frame = None
        for frame in page.frames:
            if "reactblade.portal.azure.net" in frame.url:
                # Check if this frame has the resource group name input
                try:
                    if frame.locator('input[aria-label="Resource group name"]').count() > 0:
                        form_frame = frame
                        print(f"  Found form in frame: {frame.url[:80]}")
                        break
                except Exception:
                    pass
        if form_frame is None:
            # Fallback: try any frame with a Region combobox
            for frame in page.frames:
                try:
                    if frame.locator('[aria-label="Region"]').count() > 0:
                        form_frame = frame
                        print(f"  Found form in frame: {frame.url[:80]}")
                        break
                except Exception:
                    pass
        if form_frame is None:
            raise Exception("Could not find the Create Resource Group form iframe")

        # ── STEP 3: Fill in the form ─────────────────────────────────
        print(f"STEP 3: Filling form — name={request.resource_group_name}, region={request.region}...")
        checkpoint("Fill resource group form")

        # Resource group name input
        name_input = form_frame.locator('input[aria-label="Resource group name"]').first
        if name_input.count() == 0:
            name_input = form_frame.locator('input[type="text"]').first
        name_input.click()
        page.wait_for_timeout(300)
        name_input.press("Control+a")
        name_input.type(request.resource_group_name, delay=30)
        page.wait_for_timeout(500)
        print(f"  Entered name: {request.resource_group_name}")

        # Region dropdown (it's a <DIV role="combobox" aria-label="Region">)
        region_dropdown = form_frame.locator('[role="combobox"][aria-label="Region"]').first
        if region_dropdown.count() == 0:
            region_dropdown = form_frame.locator('[aria-label*="Region"]').first
        region_dropdown.click()
        page.wait_for_timeout(1000)
        # Type the region to filter, then select
        region_option = form_frame.locator(f'[role="option"]:has-text("{request.region}")').first
        try:
            region_option.wait_for(state="visible", timeout=5000)
            region_option.click()
        except Exception:
            # Fallback: type in search if it's a searchable dropdown
            page.keyboard.type(request.region, delay=30)
            page.wait_for_timeout(1000)
            page.keyboard.press("Enter")
        page.wait_for_timeout(1000)
        print(f"  Selected region: {request.region}")

        # ── STEP 4: Click Review + create ────────────────────────────
        print("STEP 4: Clicking Review + create...")
        checkpoint("Click Review + create")
        review_btn = form_frame.locator('button:has-text("Review + create")').first
        if review_btn.count() == 0:
            review_btn = page.locator('button:has-text("Review + create"), a:has-text("Review + create")').first
        review_btn.wait_for(state="visible", timeout=10000)
        review_btn.click()
        page.wait_for_timeout(5000)
        print("  Clicked Review + create.")

        # ── STEP 5: Click Create ─────────────────────────────────
        print("STEP 5: Clicking Create...")
        checkpoint("Click the final Create button")

        # Find the Create button in the iframe (not "Review + create")
        final_create = None
        for frame in page.frames:
            if "reactblade.portal.azure.net" not in frame.url:
                continue
            for btn in frame.locator('button').all():
                try:
                    txt = btn.inner_text(timeout=500).strip()
                    if txt == "Create" and btn.is_visible():
                        final_create = btn
                        print(f"  Found Create button in iframe")
                        break
                except Exception:
                    continue
            if final_create:
                break
        if final_create is None:
            raise Exception("Could not find final Create button")
        # Use JS click — regular click doesn't always fire in iframes
        final_create.evaluate("el => el.click()")
        page.wait_for_timeout(1000)
        print("  Create clicked — deployment started.")

        print(f"\nSuccess! Created resource group '{request.resource_group_name}'.")
        return AzurePortalCreateResourceGroupResult(
            success=True,
            resource_group_name=request.resource_group_name,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return AzurePortalCreateResourceGroupResult(
            success=False,
            resource_group_name=request.resource_group_name,
            error=str(e),
        )


def test_azure_portal_create_resource_group() -> None:
    print("=" * 60)
    print("  Azure Portal – Create Resource Group")
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
            request = AzurePortalCreateResourceGroupRequest(
                resource_group_name="test-rg-001",
                region="East US",
            )
            result = azure_portal_create_resource_group(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.resource_group_name}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_azure_portal_create_resource_group)
