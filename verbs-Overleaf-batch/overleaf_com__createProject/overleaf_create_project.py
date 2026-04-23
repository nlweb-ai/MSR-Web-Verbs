"""
Playwright script (Python) — Overleaf Create Project from Template

Searches Overleaf templates for a given query, opens the first match as a new project,
and renames the project to a specified name.

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
class OverleafCreateProjectRequest:
    template_query: str
    project_name: str


@dataclass(frozen=True)
class OverleafCreateProjectResult:
    success: bool
    project_url: str
    error: str


# Searches Overleaf templates for a query string, clicks the first matching template,
# opens it as a new project, then renames the project via the toolbar dropdown menu.
# Returns the project URL on success.
def create_overleaf_project(
    page: Page,
    request: OverleafCreateProjectRequest,
) -> OverleafCreateProjectResult:

    try:
        # ── STEP 1: Navigate to Overleaf templates page ──────────────
        print("STEP 1: Loading Overleaf templates page...")
        checkpoint("Navigate to templates page")
        page.goto("https://www.overleaf.com/latex/templates", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Search for template ──────────────────────────────
        print(f'STEP 2: Searching for "{request.template_query}"...')
        search_input = page.locator('input[name="query"]')
        checkpoint("Click template search input")
        search_input.click()
        page.wait_for_timeout(500)
        search_input.press("Control+a")
        checkpoint(f"Type template query: {request.template_query}")
        search_input.type(request.template_query, delay=50)
        page.wait_for_timeout(500)
        search_input.press("Enter")
        page.wait_for_timeout(3000)
        print(f"  Search URL: {page.url}")

        # ── STEP 3: Click first template result ──────────────────────
        print("STEP 3: Clicking first template result...")
        template_links = page.locator('a[href*="/latex/templates/"]')
        found = False
        for i in range(template_links.count()):
            link = template_links.nth(i)
            text = link.inner_text(timeout=2000).strip()
            href = link.get_attribute("href") or ""
            if "/tagged/" in href or href == "/latex/templates":
                continue
            if text and len(text) > 3:
                print(f'  Found: "{text}"')
                checkpoint(f"Click template: {text[:50]}")
                link.click()
                found = True
                break
        if not found:
            return OverleafCreateProjectResult(success=False, project_url="", error="No template results found")
        page.wait_for_timeout(3000)
        print(f"  Template page: {page.url}")

        # ── STEP 4: Click "Open as Template" ─────────────────────────
        print('STEP 4: Clicking "Open as Template"...')
        open_btn = page.locator('a:has-text("Open as Template")')
        open_btn.wait_for(state="visible", timeout=5000)
        checkpoint("Click Open as Template")
        open_btn.click()
        page.wait_for_timeout(8000)
        project_url = page.url
        print(f"  Project URL: {project_url}")

        if "/project/" not in project_url:
            return OverleafCreateProjectResult(success=False, project_url="", error=f"Did not navigate to project editor: {project_url}")

        # ── STEP 5: Open project name dropdown and click Rename ──────
        print("STEP 5: Renaming project...")
        dropdown_btn = page.locator('button[aria-label="Project title options"]')
        dropdown_btn.wait_for(state="visible", timeout=5000)
        checkpoint("Open project title dropdown")
        dropdown_btn.click()
        page.wait_for_timeout(1000)

        rename_item = page.locator('a[role="menuitem"]:has-text("Rename")')
        rename_item.wait_for(state="visible", timeout=3000)
        checkpoint("Click Rename")
        rename_item.click()
        page.wait_for_timeout(1000)

        # ── STEP 6: Type new project name ────────────────────────────
        print(f'STEP 6: Setting project name to "{request.project_name}"...')
        name_input = page.locator('input.ide-redesign-toolbar-editable-project-name')
        name_input.wait_for(state="visible", timeout=3000)
        name_input.press("Control+a")
        checkpoint(f"Type project name: {request.project_name}")
        name_input.type(request.project_name, delay=30)
        name_input.press("Enter")
        page.wait_for_timeout(2000)

        title = page.title()
        print(f"  Page title: {title}")
        print(f"\nSuccess! Project URL: {project_url}")
        return OverleafCreateProjectResult(success=True, project_url=project_url, error="")

    except Exception as e:
        print(f"Error: {e}")
        return OverleafCreateProjectResult(success=False, project_url="", error=str(e))


def test_create_overleaf_project() -> None:
    request = OverleafCreateProjectRequest(
        template_query="ieee conference",
        project_name="My Paper 1",
    )

    print("=" * 60)
    print("  Overleaf – Create Project from Template")
    print(f"  Template: {request.template_query}")
    print(f"  Project name: {request.project_name}")
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
            result = create_overleaf_project(page, request)
            assert result.success, f"Create project failed: {result.error}"
            print(f"\n  SUCCESS: Project created at {result.project_url}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_create_overleaf_project)
