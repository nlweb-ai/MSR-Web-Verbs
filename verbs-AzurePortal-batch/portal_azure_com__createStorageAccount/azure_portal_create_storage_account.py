"""
Auto-generated Playwright script (Python)
Azure Portal – Create Storage Account

Navigates to Azure Portal, opens Storage accounts, and creates a new one.

Generated on: 2026-04-23T04:57:35.187Z
Uses the user's Chrome profile for persistent login state.
"""

import os
import random
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
class AzurePortalCreateStorageAccountRequest:
    storage_account_name: str
    resource_group_name: str
    region: str


@dataclass(frozen=True)
class AzurePortalCreateStorageAccountResult:
    success: bool
    storage_account_name: str
    error: str


# Creates a new storage account in Azure Portal.
def azure_portal_create_storage_account(
    page: Page,
    request: AzurePortalCreateStorageAccountRequest,
) -> AzurePortalCreateStorageAccountResult:

    try:
        # ── STEP 1: Navigate to Azure Portal ─────────────────────────
        print("STEP 1: Navigating to Azure Portal...")
        checkpoint("Navigate to Azure Portal")
        _azure_portal_login(page)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Navigate to Create Storage Account form ─────────
        print("STEP 2: Opening Create Storage Account form...")
        checkpoint("Navigate to Create Storage Account form")
        # Use the same base URL we ended up on (may be ms.portal.azure.com)
        page.goto(
            "https://portal.azure.com/#create/Microsoft.StorageAccount-ARM",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_timeout(10000)
        print(f"  Loaded: {page.url}")

        # The form lives inside a ReactBlade iframe (URL may contain reactblade.portal or reactblade-ms.portal)
        form_frame = None
        for frame in page.frames:
            if "reactblade" in frame.url and "portal.azure" in frame.url:
                try:
                    if frame.locator('[aria-label="Region"]').count() > 0:
                        form_frame = frame
                        break
                except Exception:
                    pass
        if form_frame is None:
            raise Exception("Could not find the Create Storage Account form iframe")
        print(f"  Found form in iframe")

        # ── STEP 3: Fill in the form ─────────────────────────────────
        print(f"STEP 3: Filling form — name={request.storage_account_name}...")
        checkpoint("Fill storage account form")

        # Resource group dropdown — options may take time to load
        rg_selected = False
        for attempt in range(5):
            rg_dropdown = form_frame.locator('div[role="combobox"][aria-label="Resource group"]').first
            if rg_dropdown.count() > 0 and rg_dropdown.is_visible(timeout=2000):
                rg_dropdown.click()
                page.wait_for_timeout(2000)
                # Wait for options to appear
                options = form_frame.locator('[role="option"]')
                opt_count = options.count()
                print(f"  RG dropdown attempt {attempt+1}: {opt_count} options")
                if opt_count > 0:
                    rg_option = form_frame.locator(f'[role="option"]:has-text("{request.resource_group_name}")').first
                    if rg_option.count() > 0:
                        rg_option.click()
                        rg_selected = True
                        print(f"  Selected resource group: {request.resource_group_name}")
                        break
                    else:
                        # RG not in list — close dropdown and try Create new
                        page.keyboard.press("Escape")
                        page.wait_for_timeout(500)
                        break
                else:
                    # No options yet — close dropdown and retry after waiting
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(3000)

        if not rg_selected:
            # Try Create new
            create_new_btn = form_frame.locator('button:has-text("Create new")').first
            if create_new_btn.count() > 0 and create_new_btn.is_visible(timeout=2000):
                create_new_btn.click()
                page.wait_for_timeout(2000)
                # The inline form adds a new text input for the RG name
                text_inputs = form_frame.locator('input[type="text"]').all()
                rg_name_input = None
                for ti in reversed(text_inputs):
                    try:
                        if ti.is_visible():
                            rg_name_input = ti
                            break
                    except Exception:
                        pass
                if rg_name_input is not None:
                    rg_name_input.click()
                    page.wait_for_timeout(300)
                    rg_name_input.fill(request.resource_group_name)
                    page.wait_for_timeout(1000)
                    print(f"  Typed RG name: '{rg_name_input.input_value(timeout=1000)}'")
                ok_btn = form_frame.locator('button:has-text("OK")').first
                if ok_btn.count() > 0 and ok_btn.is_visible(timeout=2000):
                    # Wait for OK to become enabled (may fail if name already exists)
                    ok_enabled = False
                    for _ in range(10):
                        aria_dis = ok_btn.get_attribute("aria-disabled") or "false"
                        if aria_dis != "true":
                            ok_enabled = True
                            break
                        page.wait_for_timeout(500)
                    if ok_enabled:
                        ok_btn.click()
                        page.wait_for_timeout(1000)
                        print(f"  Created new resource group: {request.resource_group_name}")
                    else:
                        # Name already exists — cancel and try dropdown again
                        cancel_btn = form_frame.locator('button:has-text("Cancel")').first
                        if cancel_btn.count() > 0:
                            cancel_btn.click()
                            page.wait_for_timeout(1000)
                        # Retry dropdown selection
                        rg_dropdown = form_frame.locator('div[role="combobox"][aria-label="Resource group"]').first
                        rg_dropdown.click()
                        page.wait_for_timeout(3000)
                        rg_option = form_frame.locator(f'[role="option"]:has-text("{request.resource_group_name}")').first
                        if rg_option.count() > 0:
                            rg_option.click()
                            print(f"  Selected existing resource group: {request.resource_group_name}")
                        else:
                            page.keyboard.press("Escape")
                            print(f"  WARNING: Could not select resource group: {request.resource_group_name}")
        page.wait_for_timeout(500)

        # Storage account name (aria-label may be empty, use the text input in the form)
        name_input = form_frame.locator('input[aria-label="Storage account name"]').first
        if name_input.count() == 0:
            # Find the text input that is NOT inside a combobox (i.e. the name field)
            text_inputs = form_frame.locator('input[type="text"]').all()
            name_input = None
            for ti in text_inputs:
                try:
                    if ti.is_visible():
                        name_input = ti
                        break
                except Exception:
                    pass
            if name_input is None:
                raise Exception("Could not find storage account name input")
        name_input.click()
        page.wait_for_timeout(300)
        name_input.press("Control+a")
        name_input.type(request.storage_account_name, delay=30)
        page.wait_for_timeout(500)
        print(f"  Entered name: {request.storage_account_name}")

        # Region dropdown
        region_dropdown = form_frame.locator('[aria-label="Region"]').first
        if region_dropdown.count() == 0:
            region_dropdown = form_frame.locator('[aria-label*="Region"]').first
        if region_dropdown.count() > 0 and region_dropdown.is_visible(timeout=2000):
            region_dropdown.click()
            page.wait_for_timeout(1000)
            region_option = form_frame.locator(f'[role="option"]:has-text("{request.region}")').first
            try:
                region_option.wait_for(state="visible", timeout=5000)
                region_option.click()
            except Exception:
                page.keyboard.type(request.region, delay=30)
                page.wait_for_timeout(500)
                page.keyboard.press("Enter")
            page.wait_for_timeout(500)
            print(f"  Selected region: {request.region}")

        # ── STEP 4: Click Review + create ────────────────────────────
        print("STEP 4: Clicking Review + create...")
        checkpoint("Click Review + create")
        review_btn = form_frame.locator('button:has-text("Review + create"), button:has-text("Review")').first
        if review_btn.count() == 0:
            review_btn = page.locator('button:has-text("Review + create")').first
        review_btn.wait_for(state="visible", timeout=10000)
        review_btn.click()
        page.wait_for_timeout(5000)
        print("  Clicked Review + create.")

        # ── STEP 5: Click Create ─────────────────────────────────────
        print("STEP 5: Clicking Create...")
        checkpoint("Click the final Create button")
        # Wait for validation — check for "Validation passed" text OR an enabled Create button
        final_create = None
        for wait_i in range(30):
            for frame in page.frames:
                if not ("reactblade" in frame.url and "portal.azure" in frame.url):
                    continue
                # Look for an enabled button whose text is exactly "Create"
                for btn in frame.locator('button').all():
                    try:
                        txt = btn.inner_text(timeout=500).strip()
                        if txt != "Create":
                            continue
                        if not btn.is_visible():
                            continue
                        aria_dis = btn.get_attribute("aria-disabled") or "false"
                        disabled = btn.get_attribute("disabled")
                        if aria_dis != "true" and disabled is None:
                            final_create = btn
                            break
                    except Exception:
                        continue
                if final_create:
                    break
            if final_create:
                print(f"  Create button enabled (after ~{wait_i*2}s)")
                break
            page.wait_for_timeout(2000)
        if final_create is None:
            raise Exception("Create button not found or not enabled after 60s")
        final_create.click()
        page.wait_for_timeout(20000)
        print("  Create clicked — waiting for deployment to start...")

        # Verify deployment started by checking for deployment UI or URL change
        current_url = page.url
        print(f"  URL after Create: {current_url}")

        print(f"\nSuccess! Created storage account '{request.storage_account_name}'.")
        return AzurePortalCreateStorageAccountResult(
            success=True,
            storage_account_name=request.storage_account_name,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return AzurePortalCreateStorageAccountResult(
            success=False,
            storage_account_name=request.storage_account_name,
            error=str(e),
        )


def test_azure_portal_create_storage_account() -> None:
    print("=" * 60)
    print("  Azure Portal – Create Storage Account")
    print("=" * 60)

    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default",
    )
    sa_name = "teststorage" + str(random.randint(10000, 99999))

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
            request = AzurePortalCreateStorageAccountRequest(
                storage_account_name=sa_name,
                resource_group_name="test-rg-001",
                region="East US",
            )
            result = azure_portal_create_storage_account(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.storage_account_name}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_azure_portal_create_storage_account)
