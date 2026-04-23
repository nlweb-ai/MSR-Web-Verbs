"""
Auto-generated Playwright script (Python)
Drugs.com – Drug Information
Drug: "ibuprofen"

Generated on: 2026-04-18T05:11:27.211Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class DrugRequest:
    drug: str = "ibuprofen"


@dataclass
class DrugResult:
    name: str = ""
    generic_name: str = ""
    drug_class: str = ""
    common_uses: str = ""
    side_effects: str = ""
    dosage: str = ""


def drugs_search(page: Page, request: DrugRequest) -> DrugResult:
    """Search Drugs.com for drug information."""
    print(f"  Drug: {request.drug}\n")

    url = f"https://www.drugs.com/{request.drug}.html"
    print(f"Loading {url}...")
    checkpoint("Navigate to drug page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract drug information")
    body_text = page.evaluate("document.body.innerText") or ""

    name = request.drug.title()
    generic_name = ""
    drug_class = ""
    common_uses = ""
    side_effects = ""
    dosage = ""

    try:
        h1 = page.locator("h1").first
        if h1.is_visible(timeout=2000):
            name = h1.inner_text().strip()
    except Exception:
        pass

    gm = re.search(r"(?:Generic\s*[Nn]ame|generic)[:\s]+([\w\s-]+)", body_text)
    if gm:
        generic_name = gm.group(1).strip()[:100]

    cm = re.search(r"(?:Drug\s*[Cc]lass|class)[:\s]+([\w\s,/-]+)", body_text)
    if cm:
        drug_class = cm.group(1).strip()[:100]

    um = re.search(r"(?:used\s+(?:for|to))[:\s]+(.+?)(?:\.|\n)", body_text, re.IGNORECASE)
    if um:
        common_uses = um.group(1).strip()[:200]

    sm = re.search(r"(?:side\s+effects?)[:\s]+(.+?)(?:\.|\n)", body_text, re.IGNORECASE)
    if sm:
        side_effects = sm.group(1).strip()[:200]

    dm = re.search(r"(?:dosage|dose)[:\s]+(.+?)(?:\.|\n)", body_text, re.IGNORECASE)
    if dm:
        dosage = dm.group(1).strip()[:200]

    result = DrugResult(
        name=name, generic_name=generic_name, drug_class=drug_class,
        common_uses=common_uses, side_effects=side_effects, dosage=dosage,
    )

    print("\n" + "=" * 60)
    print(f"Drugs.com: {result.name}")
    print("=" * 60)
    print(f"  Generic Name:  {result.generic_name}")
    print(f"  Drug Class:    {result.drug_class}")
    print(f"  Common Uses:   {result.common_uses[:80]}...")
    print(f"  Side Effects:  {result.side_effects[:80]}...")
    print(f"  Dosage:        {result.dosage[:80]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("drugs_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = drugs_search(page, DrugRequest())
            print(f"\nReturned info for {result.name}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
