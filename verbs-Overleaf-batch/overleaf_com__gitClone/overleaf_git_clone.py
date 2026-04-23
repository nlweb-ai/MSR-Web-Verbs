"""Playwright + Git CLI script (Python) — Overleaf Git Clone

Looks up an Overleaf project ID from the dashboard and clones it
locally via Overleaf's Git backend.

Uses the user's Chrome profile for persistent login state (browser part)
and subprocess for git operations (CLI part).
"""

import os
import re
import subprocess
from dataclasses import dataclass
from urllib.parse import quote
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class OverleafGitCloneRequest:
    search_query: str
    local_dir: str
    overleaf_git_token: str


@dataclass(frozen=True)
class OverleafGitCloneResult:
    success: bool
    project_id: str
    local_path: str
    error: str


# Looks up an Overleaf project by name on the dashboard, extracts
# the project ID, and clones it locally via git.overleaf.com.
def overleaf_git_clone(
    page: Page,
    request: OverleafGitCloneRequest,
) -> OverleafGitCloneResult:

    project_id = ""
    local_path = ""

    try:
        # ── STEP 1: Navigate to Overleaf project dashboard ───────────
        print("STEP 1: Loading Overleaf project dashboard...")
        checkpoint("Navigate to project dashboard")
        page.goto(
            "https://www.overleaf.com/project",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(2000)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Search for project ───────────────────────────────
        print(f'STEP 2: Searching for "{request.search_query}"...')
        search_input = page.locator(
            'input[placeholder="Search in all projects\u2026"]'
        ).first
        checkpoint("Click search input")
        search_input.click()
        page.wait_for_timeout(500)
        search_input.press("Control+a")
        checkpoint(f"Type search query: {request.search_query}")
        search_input.type(request.search_query, delay=50)
        page.wait_for_timeout(2000)
        print("  Search entered, waiting for results...")

        # ── STEP 3: Click the first matching project ─────────────────
        print("STEP 3: Clicking first matching project...")
        project_links = page.locator('td a[href^="/project/"]')
        count = project_links.count()
        print(f"  Found {count} project link(s)")

        if count == 0:
            return OverleafGitCloneResult(
                success=False,
                project_id="",
                local_path="",
                error=f'No projects found matching "{request.search_query}"',
            )

        first_link = project_links.first
        href = first_link.get_attribute("href") or ""
        project_name = first_link.inner_text(timeout=2000).strip()
        print(f'  Clicking: "{project_name}" (href={href})')
        checkpoint(f"Click project: {project_name}")
        first_link.click()
        page.wait_for_timeout(5000)

        # ── STEP 4: Extract project ID from URL ─────────────────────
        print("STEP 4: Extracting project ID from URL...")
        current_url = page.url
        match = re.search(r"/project/([a-f0-9]+)", current_url)
        if not match:
            return OverleafGitCloneResult(
                success=False,
                project_id="",
                local_path="",
                error=f"Could not extract project ID from URL: {current_url}",
            )
        project_id = match.group(1)
        print(f"  Project ID: {project_id}")

    except Exception as e:
        print(f"Browser error: {e}")
        return OverleafGitCloneResult(
            success=False,
            project_id=project_id,
            local_path="",
            error=f"Browser error: {e}",
        )

    # ── Browser part done — now git CLI ──────────────────────────────
    overleaf_clone_url = f"https://git.overleaf.com/{project_id}"
    local_path = os.path.abspath(request.local_dir)

    try:
        # ── STEP 5: git clone from Overleaf ──────────────────────────
        print(f"STEP 5: Cloning from {overleaf_clone_url} into {local_path}...")
        checkpoint(f"git clone {overleaf_clone_url}")

        # Build the authenticated URL using Overleaf Git token
        auth_url = (
            f"https://git:{quote(request.overleaf_git_token, safe='')}"
            f"@git.overleaf.com/{project_id}"
        )

        clone_result = subprocess.run(
            ["git", "clone", auth_url, local_path],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if clone_result.returncode != 0:
            return OverleafGitCloneResult(
                success=False,
                project_id=project_id,
                local_path="",
                error=f"git clone failed: {clone_result.stderr.strip()}",
            )
        print("  Clone successful.")

        print(f"\nSuccess! Cloned to {local_path}")
        return OverleafGitCloneResult(
            success=True,
            project_id=project_id,
            local_path=local_path,
            error="",
        )

    except Exception as e:
        print(f"Git error: {e}")
        return OverleafGitCloneResult(
            success=False,
            project_id=project_id,
            local_path=local_path,
            error=f"Git error: {e}",
        )


def test_overleaf_git_clone() -> None:
    from overleaf_com__createGitAuthToken.overleaf_create_git_auth_token import (
        overleaf_create_git_auth_token,
    )

    print("=" * 60)
    print("  Overleaf – Git Clone")
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
            # Generate a fresh Git auth token
            print("Generating Overleaf Git auth token...")
            token_result = overleaf_create_git_auth_token(page)
            if not token_result.success:
                print(f"\n  FAILED to generate token: {token_result.error}")
                return
            print(f"  Token generated: {token_result.token[:8]}...")

            request = OverleafGitCloneRequest(
                search_query="My Paper 1",
                local_dir=r"D:\tmp\my-paper-1",
                overleaf_git_token=token_result.token,
            )
            print(f"  Search: {request.search_query}")
            print(f"  Local dir: {request.local_dir}")

            result = overleaf_git_clone(page, request)
            if result.success:
                print(f"\n  SUCCESS: Cloned to {result.local_path}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_overleaf_git_clone)
