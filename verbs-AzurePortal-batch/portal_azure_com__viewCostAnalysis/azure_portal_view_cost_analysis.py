"""
Auto-generated Playwright script (Python)
Azure Portal – View Cost Analysis

Navigates to Azure Portal Cost Management > Cost analysis and extracts the
current billing period's total cost.

Generated on: 2026-04-23T04:27:18.248Z

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
class AzurePortalViewCostAnalysisRequest:
    pass  # no parameters needed


@dataclass(frozen=True)
class AzurePortalViewCostAnalysisResult:
    success: bool
    cost_amount: str
    currency: str
    error: str


# Navigates to Azure Portal Cost Management > Cost analysis and extracts the total cost.
def azure_portal_view_cost_analysis(
    page: Page,
    request: AzurePortalViewCostAnalysisRequest,
) -> AzurePortalViewCostAnalysisResult:

    try:
        # ── STEP 1: Navigate to Azure Portal ─────────────────────────
        print("STEP 1: Navigating to Azure Portal...")
        checkpoint("Navigate to Azure Portal")
        _azure_portal_login(page)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Navigate to Cost analysis ────────────────────────
        print("STEP 2: Navigating to Cost analysis...")
        checkpoint("Navigate to Cost analysis")
        page.goto(
            "https://portal.azure.com/#view/Microsoft_Azure_CostManagement/Menu/~/costanalysis",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_timeout(15000)
        print(f"  Loaded: {page.url}")

        # ── STEP 3: Open Accumulated costs view ──────────────────────
        print("STEP 3: Opening Accumulated costs view...")
        checkpoint("Open Accumulated costs view")
        # Find the reactblade iframe with the cost analysis UI
        form_frame = None
        for f in page.frames:
            if "reactblade" in f.url and "portal.azure" in f.url:
                try:
                    txt = f.locator('body').inner_text(timeout=3000)
                    if 'view' in txt.lower() or 'cost' in txt.lower():
                        form_frame = f
                        break
                except Exception:
                    pass
        if form_frame is None:
            raise Exception("Could not find cost analysis iframe")

        # Click "All views" tab, then "Accumulated costs"
        all_views_btn = form_frame.locator('button:has-text("All views")').first
        if all_views_btn.count() > 0 and all_views_btn.is_visible(timeout=5000):
            all_views_btn.click()
            page.wait_for_timeout(2000)
        acc_costs = form_frame.locator('a:has-text("Accumulated costs")').first
        if acc_costs.count() > 0 and acc_costs.is_visible(timeout=5000):
            acc_costs.click()
            page.wait_for_timeout(15000)
            print("  Opened Accumulated costs view.")
        else:
            # Try other views
            for view_name in ["Cost by resource", "Daily costs", "Cost by service"]:
                vl = form_frame.locator(f'a:has-text("{view_name}")').first
                try:
                    if vl.count() > 0 and vl.is_visible(timeout=2000):
                        vl.click()
                        page.wait_for_timeout(15000)
                        print(f"  Opened {view_name} view.")
                        break
                except Exception:
                    continue

        # ── STEP 4: Extract total cost ───────────────────────────────
        print("STEP 4: Extracting total cost...")
        checkpoint("Extract total cost")
        import re
        cost_text = ""
        # Check all frames (cost view opens in a new iframe)
        for f in page.frames:
            try:
                body_text = f.locator("body").inner_text(timeout=5000)
                matches = re.findall(r'\$[\d,]+\.?\d*', body_text)
                if matches:
                    cost_text = matches[0]
                    break
            except Exception:
                pass

        # Parse currency and amount
        cost_text = cost_text.strip()
        currency = ""
        amount = cost_text
        if cost_text.startswith("$"):
            currency = "USD"
            amount = cost_text[1:].strip()
        elif cost_text.startswith("€"):
            currency = "EUR"
            amount = cost_text[1:].strip()
        elif cost_text.startswith("£"):
            currency = "GBP"
            amount = cost_text[1:].strip()

        print(f"  Cost: {amount} {currency}")

        print(f"\nSuccess! Extracted cost: {amount} {currency}")
        return AzurePortalViewCostAnalysisResult(
            success=True,
            cost_amount=amount,
            currency=currency,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return AzurePortalViewCostAnalysisResult(
            success=False,
            cost_amount="",
            currency="",
            error=str(e),
        )


def test_azure_portal_view_cost_analysis() -> None:
    print("=" * 60)
    print("  Azure Portal – View Cost Analysis")
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
            request = AzurePortalViewCostAnalysisRequest()
            result = azure_portal_view_cost_analysis(page, request)
            if result.success:
                print(f"\n  SUCCESS: Cost = {result.cost_amount} {result.currency}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_azure_portal_view_cost_analysis)
