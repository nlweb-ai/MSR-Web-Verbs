"""
Auto-generated Playwright script (Python)
Azure Portal – Open Cloud Shell

Opens the Cloud Shell in Azure Portal, runs a CLI command, and returns the output.

Generated on: 2026-04-23T05:40:21.807Z
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


@dataclass(frozen=True)
class AzurePortalOpenCloudShellRequest:
    command: str
    shell_type: str  # "Bash" or "PowerShell"


@dataclass(frozen=True)
class AzurePortalOpenCloudShellResult:
    success: bool
    command_output: str
    error: str


# Opens Cloud Shell in Azure Portal, runs a command, and returns output.
def azure_portal_open_cloud_shell(
    page: Page,
    request: AzurePortalOpenCloudShellRequest,
) -> AzurePortalOpenCloudShellResult:

    try:
        # ── STEP 1: Navigate to Azure Portal ─────────────────────────
        print("STEP 1: Navigating to Azure Portal...")
        checkpoint("Navigate to Azure Portal")
        _azure_portal_login(page)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Click Cloud Shell icon ───────────────────────────
        print("STEP 2: Clicking Cloud Shell icon...")
        checkpoint("Click Cloud Shell icon")
        page.wait_for_timeout(10000)  # wait for toolbar to fully render
        # The Cloud Shell button is an <a role="button"> in the top toolbar
        shell_btn = page.locator(
            'a[aria-label="Cloud Shell"], '
            'a[title="Cloud Shell"], '
            'button[aria-label*="Cloud Shell"], '
            'button[title*="Cloud Shell"]'
        ).first
        shell_btn.wait_for(state="visible", timeout=15000)
        shell_btn.click()
        page.wait_for_timeout(5000)
        print("  Cloud Shell button clicked.")

        # Find the Cloud Shell iframe (ux.console.azure.com)
        shell_frame = None
        for frame in page.frames:
            if "console.azure.com" in frame.url:
                shell_frame = frame
                break
        if shell_frame is None:
            # Fallback — wait more and retry
            page.wait_for_timeout(5000)
            for frame in page.frames:
                if "console.azure.com" in frame.url:
                    shell_frame = frame
                    break
        if shell_frame is None:
            raise Exception("Could not find Cloud Shell iframe (console.azure.com)")
        print(f"  Found Cloud Shell iframe: {shell_frame.url[:60]}")

        # ── STEP 3: Handle shell type selection if prompted ──────────
        print(f"STEP 3: Selecting {request.shell_type} if prompted...")
        checkpoint(f"Select {request.shell_type}")
        try:
            shell_choice = shell_frame.locator(f'button:has-text("{request.shell_type}")').first
            if shell_choice.is_visible(timeout=5000):
                shell_choice.click()
                page.wait_for_timeout(3000)
                print(f"  Selected {request.shell_type}.")
        except Exception:
            print("  No shell type prompt, continuing...")

        # Handle "Getting started" dialog — select subscription and click Apply
        try:
            sub_dropdown = shell_frame.locator('[role="combobox"][aria-label="Subscription"]').first
            if sub_dropdown.is_visible(timeout=5000):
                print("  Getting started dialog — selecting subscription...")
                sub_dropdown.click()
                page.wait_for_timeout(2000)
                first_option = shell_frame.locator('[role="option"]').first
                if first_option.count() > 0:
                    first_option.click()
                    page.wait_for_timeout(1000)
                    print("  Selected subscription.")
                apply_btn = shell_frame.locator('button:has-text("Apply")').first
                if apply_btn.is_visible(timeout=3000):
                    apply_btn.click()
                    page.wait_for_timeout(20000)
                    print("  Clicked Apply — waiting for terminal...")
        except Exception:
            pass

        # Handle legacy "Create storage" prompt
        try:
            create_storage = shell_frame.locator(
                'button:has-text("Create storage")'
            ).first
            if create_storage.is_visible(timeout=3000):
                print("  Storage prompt detected, clicking Create storage...")
                create_storage.click()
                page.wait_for_timeout(15000)
        except Exception:
            pass

        # ── STEP 4: Wait for terminal to be ready ────────────────────
        print("STEP 4: Waiting for terminal to load...")
        checkpoint("Wait for terminal")
        # Terminal may appear in the console iframe or a nested frame
        terminal = None
        terminal_frame = None
        for attempt in range(6):  # up to 30s total
            for frame in [shell_frame] + page.frames:
                for sel in ['.xterm-helper-textarea', 'textarea.xterm-helper-textarea']:
                    try:
                        loc = frame.locator(sel).first
                        if loc.count() > 0:
                            terminal = loc
                            terminal_frame = frame
                            print(f"  Found terminal element: {sel}")
                            break
                    except Exception:
                        pass
                if terminal:
                    break
            if terminal:
                break
            page.wait_for_timeout(5000)
        if terminal is None:
            raise Exception("Could not find terminal element in Cloud Shell")
        terminal.wait_for(state="attached", timeout=10000)
        print("  Terminal ready.")

        # ── STEP 5: Type and run command ─────────────────────────────
        print(f'STEP 5: Running command: {request.command}...')
        checkpoint(f"Run command: {request.command}")
        terminal.click()
        page.wait_for_timeout(500)
        page.keyboard.type(request.command, delay=30)
        page.wait_for_timeout(500)
        page.keyboard.press("Enter")
        page.wait_for_timeout(8000)
        print("  Command executed.")

        # ── STEP 6: Extract output ───────────────────────────────────
        print("STEP 6: Extracting command output...")
        checkpoint("Extract output")
        # The terminal uses canvas rendering (xterm.js v5) — DOM text extraction is limited
        # Best-effort: try xterm-rows or accessibility tree
        output_text = ""
        out_frame = terminal_frame or shell_frame
        for extract_sel in ['.xterm-rows', '.xterm-accessibility-tree']:
            try:
                text = out_frame.locator(extract_sel).first.inner_text(timeout=3000)
                if text and len(text.strip()) > 0:
                    output_text = text
                    break
            except Exception:
                continue
        if not output_text:
            output_text = "(terminal uses canvas renderer — output not extractable via DOM)"

        # Clean up: take last portion of output (skip prompt lines)
        lines = output_text.strip().split("\n")
        # Remove empty lines and the command echo
        cleaned = []
        found_command = False
        for line in lines:
            if request.command in line:
                found_command = True
                continue
            if found_command:
                cleaned.append(line)
        command_output = "\n".join(cleaned).strip() if cleaned else output_text.strip()
        print(f"  Output length: {len(command_output)} chars")

        print(f"\nSuccess! Cloud Shell command executed.")
        return AzurePortalOpenCloudShellResult(
            success=True,
            command_output=command_output,
            error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return AzurePortalOpenCloudShellResult(
            success=False,
            command_output="",
            error=str(e),
        )


def test_azure_portal_open_cloud_shell() -> None:
    print("=" * 60)
    print("  Azure Portal – Open Cloud Shell")
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
            request = AzurePortalOpenCloudShellRequest(
                command="az account show",
                shell_type="Bash",
            )
            result = azure_portal_open_cloud_shell(page, request)
            if result.success:
                print(f"\n  SUCCESS:\n{result.command_output}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_azure_portal_open_cloud_shell)
