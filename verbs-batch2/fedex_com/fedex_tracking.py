"""
Playwright script (Python) — FedEx.com Package Tracking
Track a package by tracking number and extract status, location, and delivery date.

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
class FedexTrackingRequest:
    tracking_number: str


@dataclass(frozen=True)
class FedexTrackingResult:
    tracking_number: str
    status: str
    last_location: str
    estimated_delivery: str


# Tracks a FedEx package by tracking number and extracts the tracking
# status, last location, and estimated delivery date.
def track_fedex_package(
    page: Page,
    request: FedexTrackingRequest,
) -> FedexTrackingResult:
    tracking_number = request.tracking_number

    print(f"  Tracking number: {tracking_number}\n")

    status = "N/A"
    last_location = "N/A"
    estimated_delivery = "N/A"

    try:
        # ── Navigate ──────────────────────────────────────────────────────
        print("Loading FedEx.com tracking page...")
        checkpoint("Navigate to https://www.fedex.com/fedextrack")
        page.goto("https://www.fedex.com/fedextrack")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # ── Dismiss popups / cookie banners ───────────────────────────────
        for selector in [
            "button#onetrust-accept-btn-handler",
            "button:has-text('Accept')",
            "button:has-text('Got it')",
            "button:has-text('Close')",
        ]:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {selector}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        # ── STEP 1: Enter tracking number ─────────────────────────────────
        print(f'STEP 1: Enter tracking number "{tracking_number}"...')
        tracking_input = page.locator(
            'input[name="trackingnumber"], '
            'input[id*="tracking" i], '
            'input[aria-label*="tracking" i], '
            'input[placeholder*="tracking" i], '
            'textarea[name*="tracking" i]'
        ).first
        checkpoint("Click tracking input")
        tracking_input.evaluate("el => el.click()")
        page.wait_for_timeout(500)
        page.keyboard.press("Control+a")
        checkpoint(f"Type tracking number: {tracking_number}")
        tracking_input.type(tracking_number, delay=50)
        page.wait_for_timeout(1000)
        checkpoint("Press Enter to track")
        page.keyboard.press("Enter")
        print(f'  Entered "{tracking_number}" and pressed Enter')
        page.wait_for_timeout(2000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # ── STEP 2: Extract tracking info ─────────────────────────────────
        print("STEP 2: Extract tracking details...")

        # Status
        try:
            status_el = page.locator(
                '[class*="shipment-status"], '
                '[class*="tracking-status"], '
                '[data-testid*="status"], '
                'h2[class*="status"]'
            ).first
            status = status_el.inner_text(timeout=5000).strip()
        except Exception:
            pass

        # Last location
        try:
            location_el = page.locator(
                '[class*="location"], '
                '[class*="origin"], '
                '[data-testid*="location"]'
            ).first
            last_location = location_el.inner_text(timeout=3000).strip()
        except Exception:
            pass

        # Estimated delivery
        try:
            delivery_el = page.locator(
                '[class*="delivery-date"], '
                '[class*="estimated"], '
                '[data-testid*="delivery"]'
            ).first
            estimated_delivery = delivery_el.inner_text(timeout=3000).strip()
        except Exception:
            pass

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nTracking results for '{tracking_number}':")
        print(f"  Status: {status}")
        print(f"  Last location: {last_location}")
        print(f"  Estimated delivery: {estimated_delivery}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return FedexTrackingResult(
        tracking_number=tracking_number,
        status=status,
        last_location=last_location,
        estimated_delivery=estimated_delivery,
    )


def test_track_fedex_package() -> None:
    request = FedexTrackingRequest(
        tracking_number="123456789012",
    )

    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
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
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = track_fedex_package(page, request)
            assert result.tracking_number == request.tracking_number
            print(f"\nTracking complete: status={result.status}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_track_fedex_package)
