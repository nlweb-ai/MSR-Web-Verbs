"""
Playwright script (Python) — UPS Package Tracking
Track a package and extract status, location, delivery date, and received by.

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
class UpsTrackingRequest:
    tracking_number: str


@dataclass(frozen=True)
class UpsTrackingResult:
    tracking_number: str
    status: str
    location: str
    delivery_date: str
    received_by: str


# Tracks a UPS package by tracking number and extracts
# the status, location, delivery date, and received-by information.
def track_ups_package(
    page: Page,
    request: UpsTrackingRequest,
) -> UpsTrackingResult:
    tracking_number = request.tracking_number

    print(f"  Tracking number: {tracking_number}\n")

    status = "N/A"
    location = "N/A"
    delivery_date = "N/A"
    received_by = "N/A"

    try:
        checkpoint("Navigate to https://www.ups.com/track")
        page.goto("https://www.ups.com/track")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(4000)

        ta = page.locator('#stApp_trackingNumber')
        checkpoint(f"Fill tracking number: {tracking_number}")
        ta.fill(tracking_number)
        page.wait_for_timeout(1000)
        checkpoint("Click Track button")
        page.locator('#stApp_btnTrack').click()
        page.wait_for_timeout(5000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        body = page.locator("body").inner_text(timeout=5000)
        lines = [l.strip() for l in body.split("\n") if l.strip()]

        for i, line in enumerate(lines):
            if line == "Delivered To" and i + 1 < len(lines):
                location = lines[i + 1]
            if line.startswith("Received By") and i + 1 < len(lines):
                received_by = lines[i + 1]
            if line == "Current Event" and i + 1 < len(lines):
                status = lines[i + 1]
                for j in range(i + 2, min(i + 4, len(lines))):
                    if re.search(r'\d{2}/\d{2}/\d{4}', lines[j]):
                        delivery_date = lines[j].replace('\xa0', ' ')
                        break

        if status == "N/A":
            for i, line in enumerate(lines):
                if line in ("Delivered", "In Transit", "Out for Delivery", "Label Created", "On the Way", "Order Processed"):
                    status = line
                    break
                m = re.match(r'^(Delivered|In Transit|Out for Delivery|Label Created|On the Way|Order Processed)\s+(check_circle|info|warning|error)', line)
                if m:
                    status = m.group(1)
                    break

        if delivery_date == "N/A":
            for i, line in enumerate(lines):
                if re.search(r'\d{2}/\d{2}/\d{4}', line):
                    delivery_date = line.replace('\xa0', ' ')
                    break
                if ("scheduled delivery" in line.lower() or "expected delivery" in line.lower()) and i + 1 < len(lines):
                    delivery_date = lines[i + 1]

        print(f"Tracking: {tracking_number}")
        print(f"  Status:        {status}")
        print(f"  Location:      {location}")
        print(f"  Received By:   {received_by}")
        print(f"  Delivery Date: {delivery_date}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return UpsTrackingResult(tracking_number=tracking_number, status=status, location=location, delivery_date=delivery_date, received_by=received_by)


def test_track_ups_package() -> None:
    request = UpsTrackingRequest(tracking_number="1Z999AA10123456784")
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
            result = track_ups_package(page, request)
            assert result.tracking_number == request.tracking_number
            print(f"\nTracking complete for: {result.tracking_number}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_track_ups_package)
