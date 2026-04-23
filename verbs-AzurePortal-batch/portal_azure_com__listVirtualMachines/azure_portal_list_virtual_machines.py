"""
Auto-generated Playwright script (Python)
Azure Portal – List Virtual Machines

Navigates to Azure Portal > Virtual machines and extracts a list of VMs
with name, resource group, location, and status.

Generated on: 2026-04-23T04:27:22.898Z

Uses the user's Chrome profile for persistent login state.
"""

import os
from dataclasses import dataclass, field
from typing import List
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
class VirtualMachineInfo:
    name: str
    resource_group: str
    location: str
    status: str


@dataclass(frozen=True)
class AzurePortalListVirtualMachinesRequest:
    max_results: int


@dataclass(frozen=True)
class AzurePortalListVirtualMachinesResult:
    success: bool
    virtual_machines: tuple  # tuple of VirtualMachineInfo
    error: str


# Navigates to Azure Portal > Virtual machines and extracts the list of VMs.
def azure_portal_list_virtual_machines(
    page: Page,
    request: AzurePortalListVirtualMachinesRequest,
) -> AzurePortalListVirtualMachinesResult:

    try:
        # ── STEP 1: Navigate to Azure Portal ─────────────────────────
        print("STEP 1: Navigating to Azure Portal...")
        checkpoint("Navigate to Azure Portal")
        _azure_portal_login(page)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Navigate to Virtual machines ─────────────────────
        print("STEP 2: Navigating to Virtual machines...")
        checkpoint("Navigate to Virtual machines")
        page.goto(
            "https://portal.azure.com/#browse/Microsoft.Compute/VirtualMachines",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_timeout(15000)
        print(f"  Loaded: {page.url}")

        # ── STEP 3: Extract VM data from the table ───────────────────
        print("STEP 3: Extracting VM list...")
        checkpoint("Extract VM list")
        vms = []

        # The VM list is inside a reactblade iframe
        form_frame = None
        for f in page.frames:
            if "reactblade" in f.url and "portal.azure" in f.url:
                try:
                    txt = f.locator('body').inner_text(timeout=3000)
                    if 'virtual machine' in txt.lower() or 'no resources' in txt.lower() or 'name' in txt.lower():
                        form_frame = f
                        break
                except Exception:
                    pass

        if form_frame is None:
            # Fallback to main page
            form_frame = page

        # Check for "No resources" / "No virtual machines" message
        no_resources = form_frame.locator('text=/No (virtual machines|resources)/i').first
        try:
            if no_resources.count() > 0 and no_resources.is_visible(timeout=3000):
                print("  No virtual machines found.")
                return AzurePortalListVirtualMachinesResult(
                    success=True, virtual_machines=(), error="")
        except Exception:
            pass

        # Azure Portal renders a grid/table for the VM list
        rows = form_frame.locator(
            '[data-automationid="DetailsRow"], '
            '[role="row"]:not([role="columnheader"])'
        ).all()

        for row in rows[:request.max_results]:
            try:
                cells = row.locator('[role="gridcell"], td').all()
                if len(cells) < 4:
                    continue
                # Typical column order: checkbox, Name, Type, Resource group, Location, Status, ...
                texts = []
                for cell in cells:
                    texts.append(cell.inner_text(timeout=1000).strip())
                # Find the name cell (skip checkbox/empty cells)
                name_idx = 0
                for idx, t in enumerate(texts):
                    if t and t not in ('', '\ue73a'):  # skip checkbox/icon cells
                        name_idx = idx
                        break
                name = texts[name_idx] if name_idx < len(texts) else ""
                resource_group = texts[name_idx + 2] if name_idx + 2 < len(texts) else ""
                location = texts[name_idx + 3] if name_idx + 3 < len(texts) else ""
                status = texts[name_idx + 4] if name_idx + 4 < len(texts) else ""
                if name:
                    vms.append(VirtualMachineInfo(
                        name=name,
                        resource_group=resource_group,
                        location=location,
                        status=status,
                    ))
            except Exception:
                continue

        print(f"  Found {len(vms)} VMs.")

        print(f"\nSuccess! Listed {len(vms)} virtual machines.")
        return AzurePortalListVirtualMachinesResult(
            success=True,
            virtual_machines=tuple(vms),
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return AzurePortalListVirtualMachinesResult(
            success=False,
            virtual_machines=(),
            error=str(e),
        )


def test_azure_portal_list_virtual_machines() -> None:
    print("=" * 60)
    print("  Azure Portal – List Virtual Machines")
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
            request = AzurePortalListVirtualMachinesRequest(
                max_results=10,
            )
            result = azure_portal_list_virtual_machines(page, request)
            if result.success:
                print(f"\n  SUCCESS: {len(result.virtual_machines)} VMs found")
                for vm in result.virtual_machines:
                    print(f"    - {vm.name} | {vm.resource_group} | {vm.location} | {vm.status}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_azure_portal_list_virtual_machines)
