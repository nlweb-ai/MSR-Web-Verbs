"""
Playwright script (Python) — Mayo Clinic Condition Lookup
Look up a medical condition and extract overview, symptoms, and causes.

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
import urllib.parse
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MayoClinicConditionRequest:
    condition: str


@dataclass(frozen=True)
class MayoClinicConditionResult:
    condition: str
    overview: str
    symptoms: str
    causes: str


# Looks up a medical condition on Mayo Clinic and extracts
# the overview, symptoms, and causes sections.
def lookup_mayoclinic_condition(
    page: Page,
    request: MayoClinicConditionRequest,
) -> MayoClinicConditionResult:
    condition = request.condition

    print(f"  Condition: {condition}\n")

    overview = "N/A"
    symptoms = "N/A"
    causes = "N/A"

    try:
        search_url = f"https://www.mayoclinic.org/search/search-results?q={urllib.parse.quote(condition)}"
        checkpoint(f"Navigate to {search_url}")
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        first_link = page.locator('a[href*="/diseases-conditions/"]').first
        checkpoint("Click first diseases-conditions link")
        first_link.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        try:
            article_text = page.locator("article").first.inner_text(timeout=5000)
            ov_m = re.search(r"Overview\n(.+?)(?=\nSymptoms|\nFrom Mayo Clinic)", article_text, re.S)
            overview = ov_m.group(1).strip()[:500] if ov_m else article_text[:500]
        except Exception:
            pass

        try:
            article_text = page.locator("article").first.inner_text(timeout=5000)
            sy_m = re.search(r"Symptoms\n(.+?)(?=\nFrom Mayo Clinic|\nCauses|\nWhen to see)", article_text, re.S)
            symptoms = sy_m.group(1).strip()[:500] if sy_m else "N/A"
        except Exception:
            pass

        try:
            ca_m = re.search(r"Causes\n(.+?)(?=\nRisk factors|\nComplications|\nPrevention|\nFrom Mayo Clinic)", article_text, re.S)
            causes = ca_m.group(1).strip()[:500] if ca_m else "N/A"
        except Exception:
            pass

        print(f"Condition: {condition}")
        print(f"  Overview:  {overview[:200]}...")
        print(f"  Symptoms:  {symptoms[:200]}...")
        print(f"  Causes:    {causes[:200]}...")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return MayoClinicConditionResult(condition=condition, overview=overview, symptoms=symptoms, causes=causes)


def test_lookup_mayoclinic_condition() -> None:
    request = MayoClinicConditionRequest(condition="diabetes")
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
            result = lookup_mayoclinic_condition(page, request)
            assert result.condition == request.condition
            assert result.overview != "N/A" or result.symptoms != "N/A"
            print(f"\nCondition lookup complete for: {result.condition}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_lookup_mayoclinic_condition)
