"""
Auto-generated Playwright script (Python)
Azure Portal – View Resource Group Resources

Navigates to Azure Portal > Resource groups > [specific RG] and extracts the
list of resources (name, type, location) within it.

Generated on: 2026-04-23T04:27:38.890Z

Uses the user's Chrome profile for persistent login state.
"""

import os
from dataclasses import dataclass
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
class ResourceInfo:
    name: str
    resource_type: str
    location: str


@dataclass(frozen=True)
class AzurePortalViewResourceGroupResourcesRequest:
    resource_group_name: str
    max_resources: int


@dataclass(frozen=True)
class AzurePortalViewResourceGroupResourcesResult:
    success: bool
    resource_group_name: str
    resources: tuple  # tuple of ResourceInfo
    error: str


# Navigates to Azure Portal > Resource groups > [RG] and extracts its resources.
def azure_portal_view_resource_group_resources(
    page: Page,
    request: AzurePortalViewResourceGroupResourcesRequest,
) -> AzurePortalViewResourceGroupResourcesResult:

    try:
        # ── STEP 1: Navigate to Azure Portal ─────────────────────────
        print("STEP 1: Navigating to Azure Portal...")
        checkpoint("Navigate to Azure Portal")
        _azure_portal_login(page)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Navigate to the resource group ──────────────────
        print(f"STEP 2: Navigating to resource group '{request.resource_group_name}'...")
        checkpoint(f"Navigate to RG: {request.resource_group_name}")
        page.goto(
            "https://portal.azure.com/#view/HubsExtension/BrowseResourceGroups",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_timeout(15000)
        # Find and click the target RG in the list
        # The grid may be on the main page — find visible link for the RG
        rg_link = None
        for frame in [page] + list(page.frames):
            loc = frame.locator(f'a:has-text("{request.resource_group_name}")').first
            try:
                if loc.count() > 0 and loc.is_visible(timeout=3000):
                    rg_link = loc
                    break
            except:
                pass
        if rg_link is None:
            raise Exception(f"Could not find resource group '{request.resource_group_name}' in list")
        rg_link.click()
        page.wait_for_timeout(10000)
        print(f"  Loaded: {page.url}")

        # ── STEP 3: Extract resources from the table ─────────────────
        print("STEP 3: Extracting resources...")
        checkpoint("Extract resources")
        resources = []
        import re
        # Strip non-printable/icon Unicode chars from cell text
        def clean(t):
            t = re.sub(r'[\u0000-\u001f\ue000-\uf8ff]', '', t).strip()
            return t

        # Resources grid is in a reactblade iframe; find the one with "Type" column
        all_frames = [f for f in page.frames if "reactblade" in f.url and "portal.azure" in f.url]
        for frame in all_frames:
            grids = frame.locator('[role="grid"]').all()
            for grid in grids:
                try:
                    rows = grid.locator('[role="row"]').all()
                    if len(rows) < 2:
                        continue
                    # Check header for "Type" column
                    headers = rows[0].locator('[role="columnheader"]').all()
                    header_texts = [clean(h.inner_text(timeout=1000)) for h in headers]
                    if "Type" not in header_texts:
                        continue
                    # Found the resources grid — parse data rows
                    name_idx = header_texts.index("Name") if "Name" in header_texts else 1
                    type_idx = header_texts.index("Type") if "Type" in header_texts else 2
                    loc_idx = header_texts.index("Location") if "Location" in header_texts else 3
                    for row in rows[1:request.max_resources + 1]:
                        cells = row.locator('[role="gridcell"]').all()
                        if len(cells) <= max(name_idx, type_idx, loc_idx):
                            continue
                        name = clean(cells[name_idx].inner_text(timeout=1000))
                        rtype = clean(cells[type_idx].inner_text(timeout=1000))
                        loc = clean(cells[loc_idx].inner_text(timeout=1000)) if loc_idx < len(cells) else ""
                        if name:
                            resources.append(ResourceInfo(name=name, resource_type=rtype, location=loc))
                    if resources:
                        break
                except Exception:
                    continue
            if resources:
                break

        print(f"  Found {len(resources)} resources.")

        print(f"\nSuccess! Extracted {len(resources)} resources from '{request.resource_group_name}'.")
        return AzurePortalViewResourceGroupResourcesResult(
            success=True,
            resource_group_name=request.resource_group_name,
            resources=tuple(resources),
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return AzurePortalViewResourceGroupResourcesResult(
            success=False,
            resource_group_name=request.resource_group_name,
            resources=(),
            error=str(e),
        )


def test_azure_portal_view_resource_group_resources() -> None:
    print("=" * 60)
    print("  Azure Portal – View Resource Group Resources")
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
            request = AzurePortalViewResourceGroupResourcesRequest(
                resource_group_name="test-rg-001",
                max_resources=20,
            )
            result = azure_portal_view_resource_group_resources(page, request)
            if result.success:
                print(f"\n  SUCCESS: {len(result.resources)} resources in '{result.resource_group_name}'")
                for res in result.resources:
                    print(f"    - {res.name} | {res.resource_type} | {res.location}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_azure_portal_view_resource_group_resources)
