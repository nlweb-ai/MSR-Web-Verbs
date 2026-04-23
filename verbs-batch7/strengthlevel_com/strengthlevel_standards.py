"""
Auto-generated Playwright script (Python)
StrengthLevel – Exercise Standards

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class StandardsRequest:
    exercise_slug: str = "bench-press"
    bodyweight: int = 180


@dataclass
class StandardsResult:
    beginner: str = ""
    novice: str = ""
    intermediate: str = ""
    advanced: str = ""
    elite: str = ""


def strengthlevel_standards(page: Page, request: StandardsRequest) -> StandardsResult:
    """Look up strength standards for an exercise."""
    print(f"  Exercise: {request.exercise_slug}, Bodyweight: {request.bodyweight} lb\n")

    url = f"https://strengthlevel.com/strength-standards/{request.exercise_slug}/lb"
    print(f"Loading {url}...")
    checkpoint("Navigate to standards page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = StandardsResult()

    checkpoint("Extract standards for bodyweight")
    body = page.evaluate("document.body.innerText")

    # Find the row matching the bodyweight in the table
    # Table format: bodyweight  beginner  novice  intermediate  advanced  elite
    pattern = rf'^{request.bodyweight}\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)'
    m = re.search(pattern, body, re.MULTILINE)
    if m:
        result.beginner = m.group(1) + " lb"
        result.novice = m.group(2) + " lb"
        result.intermediate = m.group(3) + " lb"
        result.advanced = m.group(4) + " lb"
        result.elite = m.group(5) + " lb"

    print(f"  Standards for {request.bodyweight} lb male:")
    print(f"    Beginner:     {result.beginner}")
    print(f"    Novice:       {result.novice}")
    print(f"    Intermediate: {result.intermediate}")
    print(f"    Advanced:     {result.advanced}")
    print(f"    Elite:        {result.elite}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("strengthlevel")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = StandardsRequest()
            result = strengthlevel_standards(page, request)
            print("\n=== DONE ===")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
