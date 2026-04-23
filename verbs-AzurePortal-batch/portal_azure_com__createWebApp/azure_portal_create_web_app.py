"""
Auto-generated Playwright script (Python)
Azure Portal – Create Web App

Navigates to Azure Portal > App Services and creates a new Web App with the
specified name, resource group, runtime stack, region, and pricing tier.

Generated on: 2026-04-23T04:27:33.639Z

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
    """Use the top search bar to find and click a service."""
    search_box = None
    for selector in [
        'input[role="searchbox"]',
        'input[aria-label*="Search resources"]',
        'input[aria-label*="Search"]',
        '#portal-search-input',
    ]:
        loc = page.locator(selector).first
        if loc.count() > 0 and loc.is_visible(timeout=2000):
            search_box = loc
            break
    if search_box is None:
        search_trigger = page.locator(
            'button[aria-label*="Search"], [role="search"], #portal-search'
        ).first
        search_trigger.click()
        page.wait_for_timeout(1500)
        search_box = page.locator(
            'input[role="searchbox"], input[aria-label*="Search"]'
        ).first
    search_box.click()
    page.wait_for_timeout(500)
    search_box.press("Control+a")
    search_box.type(service_name, delay=30)
    page.wait_for_timeout(2000)
    for sel in [
        f'a:has-text("{service_name}")',
        f'[role="listbox"] [role="option"]:has-text("{service_name}")',
        f'[role="list"] [role="listitem"]:has-text("{service_name}")',
        f'li:has-text("{service_name}")',
    ]:
        loc = page.locator(sel).first
        try:
            if loc.count() > 0 and loc.is_visible(timeout=3000):
                loc.click()
                page.wait_for_timeout(2000)
                return
        except Exception:
            continue
    search_box.press("Enter")
    page.wait_for_timeout(3000)


@dataclass(frozen=True)
class AzurePortalCreateWebAppRequest:
    web_app_name: str
    resource_group_name: str
    runtime_stack: str
    region: str


@dataclass(frozen=True)
class AzurePortalCreateWebAppResult:
    success: bool
    web_app_name: str
    web_app_url: str
    error: str


# Creates a new Web App in Azure Portal via App Services.
def azure_portal_create_web_app(
    page: Page,
    request: AzurePortalCreateWebAppRequest,
) -> AzurePortalCreateWebAppResult:

    try:
        # ── STEP 1: Navigate to Azure Portal ─────────────────────────
        print("STEP 1: Navigating to Azure Portal...")
        checkpoint("Navigate to Azure Portal")
        _azure_portal_login(page)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Navigate to Create Web App ────────────────────
        print("STEP 2: Navigating to Create Web App...")
        checkpoint("Navigate to Create Web App")
        page.goto(
            "https://portal.azure.com/#create/Microsoft.WebSite",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_timeout(15000)
        print(f"  Loaded: {page.url}")

        # Find the form frame — may be main page or reactblade iframe
        form_frame = page
        for f in page.frames:
            if "reactblade" in f.url and "portal.azure" in f.url:
                if f.locator('input[aria-label="Web App name"]').count() > 0:
                    form_frame = f
                    break
        print(f"  Form in: {'main page' if form_frame == page else 'iframe'}")

        # ── STEP 3: Fill in the form ─────────────────────────────────
        print("STEP 3: Filling in the Create Web App form...")
        checkpoint("Fill form")

        # Helper: open Azure Portal combobox (needs Enter key, not click)
        def _open_combo(combo):
            combo.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            combo.focus()
            page.wait_for_timeout(500)
            combo.press('Enter')
            page.wait_for_timeout(2000)
            # Verify it opened
            expanded = combo.get_attribute('aria-expanded')
            if expanded != 'true':
                # Retry: click then Enter
                combo.click()
                page.wait_for_timeout(500)
                combo.press('Enter')
                page.wait_for_timeout(2000)

        def _select_combo_option(combo, option_text):
            for retry in range(3):
                _open_combo(combo)
                expanded = combo.get_attribute('aria-expanded')
                if expanded != 'true':
                    print(f"    Combo not expanded after attempt {retry+1}")
                    page.wait_for_timeout(1000)
                    continue
                ctrl_id = combo.get_attribute('aria-controls')
                if ctrl_id:
                    dialog = form_frame.locator(f'#{ctrl_id}')
                    if dialog.count() > 0 and dialog.first.is_visible(timeout=3000):
                        opt = dialog.locator(f'text="{option_text}"').first
                        if opt.count() > 0 and opt.is_visible(timeout=2000):
                            opt.click()
                            page.wait_for_timeout(1000)
                            return True
                        else:
                            # Debug: show what options exist
                            if retry == 0:
                                items = dialog.locator('*').all()
                                texts = []
                                for it in items[:30]:
                                    try:
                                        t = it.inner_text(timeout=300).strip()
                                        if t and len(t) < 50 and t not in texts:
                                            texts.append(t)
                                    except:
                                        pass
                                if texts:
                                    print(f"    Dialog options: {texts[:10]}")
                # Close and retry
                combo.press('Escape')
                page.wait_for_timeout(1000)
            return False

        # 3a. Select resource group
        print(f"  Setting resource group: {request.resource_group_name}")
        rg_combo = form_frame.locator('[role="combobox"][aria-label*="Resource group selector"]').first
        if rg_combo.count() > 0 and rg_combo.is_visible(timeout=5000):
            if _select_combo_option(rg_combo, request.resource_group_name):
                print(f"    Selected RG: {request.resource_group_name}")
            else:
                print(f"    WARNING: RG option '{request.resource_group_name}' not found")
        else:
            print("    WARNING: RG combobox not found")

        # 3b. Enter web app name
        print(f"  Setting web app name: {request.web_app_name}")
        name_input = form_frame.locator('input[aria-label="Web App name"]').first
        if name_input.count() == 0:
            name_input = form_frame.locator('input[placeholder="Web App name"]').first
        name_input.wait_for(state="visible", timeout=5000)
        name_input.click()
        name_input.press("Control+a")
        name_input.type(request.web_app_name, delay=30)
        # Wait for name validation and dependent fields to enable
        print("  Waiting for name validation...")
        page.wait_for_timeout(8000)

        # 3c. Select runtime stack (may be disabled until name is validated)
        print(f"  Setting runtime stack: {request.runtime_stack}")
        runtime_combo = form_frame.locator('[role="combobox"][aria-label="Runtime stack selector"]').first
        if runtime_combo.count() == 0:
            runtime_combo = form_frame.locator('[role="combobox"][aria-label*="Runtime stack"]').first
        if runtime_combo.count() > 0:
            # Wait for combo to become enabled (check CSS class)
            for _ in range(15):
                cls = runtime_combo.evaluate('e => e.className')
                if 'azc-disabled' not in cls:
                    break
                page.wait_for_timeout(2000)
            if _select_combo_option(runtime_combo, request.runtime_stack):
                print(f"    Selected runtime: {request.runtime_stack}")
            else:
                print(f"    WARNING: Runtime option '{request.runtime_stack}' not found")
        else:
            print("    WARNING: Runtime combobox not found")

        # 3d. Select region
        print(f"  Setting region: {request.region}")
        region_combo = form_frame.locator('[role="combobox"][aria-label="Region selector"]').first
        if region_combo.count() == 0:
            region_combo = form_frame.locator('[role="combobox"][aria-label*="Region"]').first
        if region_combo.count() > 0 and region_combo.is_visible(timeout=5000):
            if _select_combo_option(region_combo, request.region):
                print(f"    Selected region: {request.region}")
            else:
                print(f"    WARNING: Region option '{request.region}' not found")
        else:
            print("    WARNING: Region combobox not found")

        # 3e. Pricing plan — try to select Free tier
        print("  Attempting to select Free tier pricing plan...")
        try:
            pricing_link = form_frame.locator(
                'a:has-text("Explore pricing plans"), '
                'a:has-text("pricing"), '
                'button:has-text("Change size"), '
                '[aria-label*="Pricing plan"]'
            ).first
            if pricing_link.is_visible(timeout=3000):
                pricing_link.click()
                page.wait_for_timeout(2000)
                free_tier = form_frame.locator(
                    '[role="option"]:has-text("Free"), '
                    'button:has-text("Free"), '
                    'div:has-text("Free F1")'
                ).first
                if free_tier.is_visible(timeout=3000):
                    free_tier.click()
                    page.wait_for_timeout(1000)
        except Exception:
            pass

        # ── STEP 4: Click Review + create ────────────────────────────
        print("STEP 4: Clicking Review + create...")
        checkpoint("Review + create")
        # "Review + create" is a tab in this form
        review_tab = form_frame.locator('[role="tab"]:has-text("Review + create")').first
        if review_tab.count() == 0:
            review_tab = page.locator('[role="tab"]:has-text("Review + create")').first
        review_tab.wait_for(state="visible", timeout=10000)
        review_tab.click()
        page.wait_for_timeout(8000)
        print("  Validation page loaded.")

        # ── STEP 5: Click Create (exact match, wait for enabled) ─────
        print("STEP 5: Waiting for Create button to become enabled...")
        checkpoint("Click Create")
        create_clicked = False
        for attempt in range(30):
            # Search main page and iframes for "Create" — can be <button> or <div role="button">
            all_search_frames = [page] + [f for f in page.frames if "reactblade" in f.url and "portal.azure" in f.url]
            for sf in all_search_frames:
                # Check both <button> and <div role="button">
                for selector in ['button', '[role="button"]']:
                    elements = sf.locator(selector).all()
                    for el in elements:
                        try:
                            txt = el.inner_text(timeout=1000).strip()
                            if txt == "Create":
                                disabled = el.get_attribute("disabled")
                                aria_disabled = el.get_attribute("aria-disabled")
                                if disabled is None and aria_disabled != "true":
                                    el.click()
                                    print(f"  Clicked Create button (attempt {attempt + 1})")
                                    page.wait_for_timeout(5000)
                                    create_clicked = True
                                    break
                        except Exception:
                            continue
                    if create_clicked:
                        break
                if create_clicked:
                    break
            if create_clicked:
                break
            page.wait_for_timeout(2000)
        if not create_clicked:
            raise Exception("Create button did not become enabled within 60 seconds")
        print("  Deployment started.")

        # ── STEP 6: Wait for deployment ──────────────────────────────
        print("STEP 6: Waiting for deployment to complete...")
        checkpoint("Wait for deployment")
        for _ in range(30):
            page.wait_for_timeout(5000)
            try:
                complete_text = page.locator(
                    ':has-text("Your deployment is complete"), '
                    ':has-text("deployment is complete"), '
                    ':has-text("Deployment succeeded")'
                ).first
                if complete_text.is_visible(timeout=2000):
                    print("  Deployment complete!")
                    break
            except Exception:
                pass

        # Try to extract the web app URL
        web_app_url = f"https://{request.web_app_name}.azurewebsites.net"

        print(f"\nSuccess! Created web app: {request.web_app_name}")
        return AzurePortalCreateWebAppResult(
            success=True,
            web_app_name=request.web_app_name,
            web_app_url=web_app_url,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return AzurePortalCreateWebAppResult(
            success=False,
            web_app_name=request.web_app_name,
            web_app_url="",
            error=str(e),
        )


def test_azure_portal_create_web_app() -> None:
    print("=" * 60)
    print("  Azure Portal – Create Web App")
    print("=" * 60)

    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default",
    )
    random_suffix = str(random.randint(10000, 99999))
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
            request = AzurePortalCreateWebAppRequest(
                web_app_name=f"test-webapp-{random_suffix}",
                resource_group_name="test-rg-001",
                runtime_stack="Node 20 LTS",
                region="East US",
            )
            result = azure_portal_create_web_app(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.web_app_name} at {result.web_app_url}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_azure_portal_create_web_app)
