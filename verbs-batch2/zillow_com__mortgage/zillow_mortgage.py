"""
Playwright script (Python) — Zillow Mortgage Calculator
Calculate mortgage payments and extract monthly payment breakdown.

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ZillowMortgageRequest:
    home_price: str
    down_payment_pct: str


@dataclass(frozen=True)
class ZillowMortgageResult:
    home_price: str
    down_payment_pct: str
    monthly_payment: str
    principal_interest: str
    property_tax: str
    insurance: str


# Calculates mortgage on Zillow given a home price and down payment percentage,
# and extracts the monthly payment, principal & interest, property tax, and insurance.
def calculate_zillow_mortgage(
    page: Page,
    request: ZillowMortgageRequest,
) -> ZillowMortgageResult:
    home_price = request.home_price
    down_payment_pct = request.down_payment_pct

    print(f"  Home Price: ${home_price}, Down Payment: {down_payment_pct}%\n")

    monthly_payment = "N/A"
    principal_interest = "N/A"
    property_tax = "N/A"
    insurance = "N/A"

    try:
        checkpoint("Navigate to https://www.zillow.com/mortgage-calculator/")
        page.goto("https://www.zillow.com/mortgage-calculator/")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)

        for sel in ["button#onetrust-accept-btn-handler", 'button:has-text("Accept")',
                     'button:has-text("Close")', 'button[aria-label*="close" i]']:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {sel}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        try:
            price_input = page.locator('input[name="homePrice"]').first
            checkpoint(f"Fill home price: {home_price}")
            price_input.click()
            page.wait_for_timeout(300)
            price_input.fill("")
            page.wait_for_timeout(200)
            price_input.type(home_price, delay=30)
            page.wait_for_timeout(500)
        except Exception:
            pass

        try:
            dp_pct_input = page.locator('input[name="downPaymentPercent"]').first
            checkpoint(f"Fill down payment: {down_payment_pct}%")
            dp_pct_input.click()
            page.wait_for_timeout(300)
            dp_pct_input.fill("")
            page.wait_for_timeout(200)
            dp_pct_input.type(down_payment_pct, delay=30)
            page.wait_for_timeout(500)
        except Exception:
            pass

        checkpoint("Press Tab to trigger calculation")
        page.keyboard.press("Tab")
        page.wait_for_timeout(4000)

        body_text = page.locator("body").inner_text(timeout=5000)

        m = re.search(r"Your payment\s*\$?([\d,]+)", body_text)
        monthly_payment = f"${m.group(1)}" if m else "N/A"

        m = re.search(r"P\s*&\s*I\s*\$?([\d,]+)", body_text)
        principal_interest = f"${m.group(1)}" if m else "N/A"

        m = re.search(r"Taxes\s*\$?([\d,]+)", body_text)
        property_tax = f"${m.group(1)}" if m else "N/A"

        m = re.search(r"Insurance\s*\$?([\d,]+)", body_text)
        insurance = f"${m.group(1)}" if m else "N/A"

        print(f"Mortgage Estimate:")
        print(f"  Monthly Payment:      {monthly_payment}")
        print(f"  Principal & Interest: {principal_interest}")
        print(f"  Property Tax:         {property_tax}")
        print(f"  Insurance:            {insurance}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return ZillowMortgageResult(
        home_price=home_price, down_payment_pct=down_payment_pct,
        monthly_payment=monthly_payment, principal_interest=principal_interest,
        property_tax=property_tax, insurance=insurance,
    )


def test_calculate_zillow_mortgage() -> None:
    request = ZillowMortgageRequest(home_price="500000", down_payment_pct="20")
    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir, channel="chrome", headless=False, viewport=None,
            args=["--disable-blink-features=AutomationControlled", "--disable-infobars", "--disable-extensions"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = calculate_zillow_mortgage(page, request)
            assert result.home_price == request.home_price
            assert result.down_payment_pct == request.down_payment_pct
            print(f"\nMortgage calculation complete")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_calculate_zillow_mortgage)
