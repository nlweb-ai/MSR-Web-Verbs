"""
Auto-generated Playwright script (Python)
Azure Portal – Open Service

Navigates to Azure Portal, searches for a specified service, and opens it.

Generated on: 2026-04-23T04:19:14.081Z
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
class AzurePortalOpenServiceRequest:
    service_name: str


@dataclass(frozen=True)
class AzurePortalOpenServiceResult:
    success: bool
    service_name: str
    page_url: str
    error: str


# Navigates to Azure Portal and opens the specified service.
def azure_portal_open_service(
    page: Page,
    request: AzurePortalOpenServiceRequest,
) -> AzurePortalOpenServiceResult:

    try:
        # ── STEP 1: Navigate to Azure Portal ─────────────────────────
        print("STEP 1: Navigating to Azure Portal...")
        checkpoint("Navigate to Azure Portal")
        page.goto(
            "https://portal.azure.com/",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        # Azure Portal may redirect through OAuth login; wait for it to settle
        for _ in range(30):
            page.wait_for_timeout(2000)
            current_url = page.url
            if "portal.azure.com" in current_url and "login" not in current_url and "oauth" not in current_url:
                break
            # Handle "Pick an account" page
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
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Click the search bar ─────────────────────────────
        print(f'STEP 2: Searching for "{request.service_name}"...')
        checkpoint(f"Search for: {request.service_name}")

        # Azure Portal search bar: role="searchbox" or the search input
        search_box = None
        for selector in [
            'input[role="searchbox"]',
            'input[aria-label*="Search resources"]',
            'input[aria-label*="Search"]',
            '#portal-search-input',
            '[data-testid="portal-search-input"]',
        ]:
            loc = page.locator(selector).first
            if loc.count() > 0 and loc.is_visible(timeout=2000):
                search_box = loc
                break

        if search_box is None:
            # Fallback: click the search icon/area to expand the search bar
            search_trigger = page.locator(
                'button[aria-label*="Search"], '
                '[role="search"], '
                '#portal-search'
            ).first
            search_trigger.click()
            page.wait_for_timeout(1500)
            # Now try to find the input
            search_box = page.locator(
                'input[role="searchbox"], '
                'input[aria-label*="Search"]'
            ).first

        search_box.click()
        page.wait_for_timeout(500)
        search_box.press("Control+a")
        search_box.type(request.service_name, delay=30)
        page.wait_for_timeout(2000)
        print(f"  Typed: {request.service_name}")

        # ── STEP 3: Click the matching service result ────────────────
        print("STEP 3: Clicking matching service result...")
        checkpoint(f"Click service: {request.service_name}")

        # Azure Portal search results: look for a link/item matching the service name
        found = False

        # Strategy 1: look for a list item or link whose text matches the service name
        results_selectors = [
            f'a:has-text("{request.service_name}")',
            f'[role="listbox"] [role="option"]:has-text("{request.service_name}")',
            f'[role="list"] [role="listitem"]:has-text("{request.service_name}")',
            f'li:has-text("{request.service_name}")',
            f'div[role="option"]:has-text("{request.service_name}")',
        ]
        for sel in results_selectors:
            loc = page.locator(sel).first
            try:
                if loc.count() > 0 and loc.is_visible(timeout=3000):
                    loc.click()
                    found = True
                    break
            except Exception:
                continue

        # Strategy 2: press Enter to submit the search
        if not found:
            print("  No direct result match, pressing Enter...")
            search_box.press("Enter")
            page.wait_for_timeout(3000)

            # On the search results page, find the matching item
            for sel in [
                f'a:has-text("{request.service_name}")',
                f'[role="link"]:has-text("{request.service_name}")',
                f'button:has-text("{request.service_name}")',
            ]:
                loc = page.locator(sel).first
                try:
                    if loc.count() > 0 and loc.is_visible(timeout=3000):
                        loc.click()
                        found = True
                        break
                except Exception:
                    continue

        if not found:
            raise Exception(f"Could not find service '{request.service_name}' in search results")

        page.wait_for_timeout(5000)
        print(f"  Navigated to service page.")

        # ── STEP 4: Capture the result URL ───────────────────────────
        print("STEP 4: Capturing result...")
        final_url = page.url
        print(f"  URL: {final_url}")

        print(f"\nSuccess! Opened '{request.service_name}' at {final_url}")
        return AzurePortalOpenServiceResult(
            success=True,
            service_name=request.service_name,
            page_url=final_url,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return AzurePortalOpenServiceResult(
            success=False,
            service_name=request.service_name,
            page_url="",
            error=str(e),
        )


def test_azure_portal_open_service() -> None:
    print("=" * 60)
    print("  Azure Portal – Open Service")
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
            request = AzurePortalOpenServiceRequest(
                service_name="Azure OpenAI",
            )
            result = azure_portal_open_service(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.service_name} at {result.page_url}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_azure_portal_open_service)
