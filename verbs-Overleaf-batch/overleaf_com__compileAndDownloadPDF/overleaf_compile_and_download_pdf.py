"""
Auto-generated Playwright script (Python)
Overleaf – Compile and Download PDF

Navigates to a project by ID, recompiles it, and downloads
the resulting PDF.

Generated on: 2026-04-21T21:06:16.425Z
Recorded 4 browser interactions

Uses the user's Chrome profile for persistent login state.
"""

import os
import importlib.util
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


def ensure_test_project_exists(page: Page, project_name: str = "My Paper 1") -> str:
    """Check if a project exists on the Overleaf dashboard. If not, create one.

    Returns the project_id extracted from the project URL.
    """
    page.goto(
        "https://www.overleaf.com/project",
        wait_until="domcontentloaded",
        timeout=30000,
    )
    page.wait_for_timeout(3000)

    search_input = page.locator(
        'input[placeholder="Search in all projects\u2026"]'
    ).first
    search_input.click()
    page.wait_for_timeout(500)
    search_input.press("Control+a")
    search_input.type(project_name, delay=50)
    page.wait_for_timeout(2000)

    links = page.locator('td a[href^="/project/"]')
    if links.count() > 0:
        href = links.first.get_attribute("href")
        project_id = href.split("/project/")[-1]
        print(f"  Project '{project_name}' found (id={project_id})")
        return project_id

    print(f"  Project '{project_name}' not found, creating...")
    spec = importlib.util.spec_from_file_location(
        "create_proj",
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "overleaf_com__createProject",
            "overleaf_create_project.py",
        ),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    result = mod.create_overleaf_project(
        page,
        mod.OverleafCreateProjectRequest(
            template_query="ieee conference",
            project_name=project_name,
        ),
    )
    if not result.success:
        raise RuntimeError(f"Failed to create project: {result.error}")
    project_id = result.project_url.split("/project/")[-1]
    print(f"  Created project '{project_name}' (id={project_id})")
    return project_id


@dataclass(frozen=True)
class OverleafCompileAndDownloadPDFRequest:
    project_id: str
    download_dir: str


@dataclass(frozen=True)
class OverleafCompileAndDownloadPDFResult:
    success: bool
    pdf_file_path: str
    error: str


# Navigates to a project by ID, recompiles, and downloads the PDF.
def overleaf_compile_and_download_pdf(
    page: Page,
    request: OverleafCompileAndDownloadPDFRequest,
) -> OverleafCompileAndDownloadPDFResult:

    try:
        # ── STEP 1: Navigate to project editor ──────────────────────
        print("STEP 1: Loading project editor...")
        checkpoint("Navigate to project editor")
        page.goto(
            f"https://www.overleaf.com/project/{request.project_id}",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(8000)
        print(f"  Loaded: {page.url}")

        # ── STEP 2: Click Recompile button ───────────────────────────
        print("STEP 2: Clicking Recompile...")
        recompile_btn = page.locator('button:has-text("Recompile")').first
        if recompile_btn.count() == 0:
            recompile_btn = page.locator('button[aria-label="Recompile"]').first
        checkpoint("Click Recompile button")
        recompile_btn.click()
        page.wait_for_timeout(15000)
        print("  Compilation complete.")

        # ── STEP 3: Click the Download PDF button ─────────────────
        print("STEP 3: Clicking Download PDF...")
        # The visible download button is an <a> with aria-label="Download PDF"
        download_pdf = page.locator('a[aria-label="Download PDF"]').first
        checkpoint("Click Download PDF")
        with page.expect_download() as download_info:
            download_pdf.click()
        download = download_info.value
        pdf_path = os.path.join(
            request.download_dir, download.suggested_filename,
        )
        download.save_as(pdf_path)
        page.wait_for_timeout(2000)
        print(f"  Downloaded: {pdf_path}")

        print(f"\nSuccess! PDF downloaded: {pdf_path}")
        return OverleafCompileAndDownloadPDFResult(
            success=True, pdf_file_path=pdf_path, error="",
        )

    except Exception as e:
        print(f"Error: {e}")
        return OverleafCompileAndDownloadPDFResult(
            success=False, pdf_file_path="", error=str(e),
        )


def test_overleaf_compile_and_download_pdf() -> None:
    print("=" * 60)
    print("  Overleaf – Compile and Download PDF")
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
            project_id = ensure_test_project_exists(page, "My Paper 1")
            request = OverleafCompileAndDownloadPDFRequest(
                project_id=project_id,
                download_dir=os.path.join(os.environ["USERPROFILE"], "Downloads"),
            )
            result = overleaf_compile_and_download_pdf(page, request)
            if result.success:
                print(f"\n  SUCCESS: {result.pdf_file_path}")
            else:
                print(f"\n  FAILED: {result.error}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_overleaf_compile_and_download_pdf)
