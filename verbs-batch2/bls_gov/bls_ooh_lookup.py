"""
Playwright script (Python) — BLS.gov Occupational Outlook Handbook Lookup
Search for an occupation and extract median pay, job outlook, and education.

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
from urllib.parse import quote
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BlsOohRequest:
    occupation: str


@dataclass(frozen=True)
class BlsOohResult:
    occupation: str
    median_pay: str
    job_outlook: str
    entry_level_education: str


# Searches the BLS Occupational Outlook Handbook for a given occupation
# and extracts the median pay, job outlook, and entry-level education.
def lookup_bls_ooh(
    page: Page,
    request: BlsOohRequest,
) -> BlsOohResult:
    occupation = request.occupation

    print(f"  Occupation: {occupation}\n")

    median_pay = "N/A"
    job_outlook = "N/A"
    entry_level_education = "N/A"

    try:
        # ── Navigate to OOH search ───────────────────────────────────────
        print("Loading BLS Occupational Outlook Handbook search...")
        search_url = f"https://data.bls.gov/search/query/results?cx=013738036195919377644%3A6ih0hfrgl50&q={quote(occupation)}+inurl%3Abls.gov%2Fooh%2F"
        checkpoint(f"Navigate to BLS search for {occupation}")
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # ── STEP 1: Click the first OOH result ───────────────────────────
        print(f'STEP 1: Find "{occupation}" in search results...')
        ooh_links = page.locator('a[href*="/ooh/"][href*=".htm"]')
        count = ooh_links.count()
        href = None
        for i in range(count):
            link = ooh_links.nth(i)
            h = link.get_attribute("href")
            if h and "/ooh/" in h and h.endswith(".htm"):
                link_text = link.inner_text(timeout=2000).strip()
                print(f'  Found: "{link_text}"')
                href = h if h.startswith("http") else f"https://www.bls.gov{h}"
                break

        if not href:
            print("  No occupation link found, trying first /ooh/ link")
            href = ooh_links.first.get_attribute("href")
            if href and not href.startswith("http"):
                href = f"https://www.bls.gov{href}"

        checkpoint(f"Navigate to occupation page: {href}")
        page.goto(href)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        # ── STEP 2: Extract from Quick Facts table ────────────────────────
        print("STEP 2: Extract from Quick Facts table...")

        table_text = ""
        try:
            table = page.locator('table').first
            table_text = table.inner_text(timeout=5000)
        except Exception:
            pass

        if not table_text:
            table_text = page.locator("body").inner_text(timeout=10000)

        # Median pay
        mp = re.search(r"20\d{2} Median Pay\s+(\$[\d,]+\s+per\s+\w+)", table_text)
        if mp:
            median_pay = mp.group(1).strip()
        else:
            mp2 = re.search(r"\$([\d,]+)\s+per\s+year", table_text)
            if mp2:
                median_pay = mp2.group(0).strip()

        # Job outlook
        jo = re.search(r"Job Outlook,\s*\d{4}.\d{2,4}\s+(.+)", table_text)
        if jo:
            job_outlook = jo.group(1).strip()
        else:
            jo2 = re.search(r"(\d+%\s*\([^)]+\))", table_text)
            if jo2:
                job_outlook = jo2.group(1).strip()

        # Entry-level education
        edu = re.search(r"Typical Entry[- ]Level Education\s+(.+)", table_text)
        if edu:
            entry_level_education = edu.group(1).strip()

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nResults for '{occupation}':")
        print(f"  Median Pay:            {median_pay}")
        print(f"  Job Outlook:           {job_outlook}")
        print(f"  Entry-Level Education: {entry_level_education}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return BlsOohResult(
        occupation=occupation,
        median_pay=median_pay,
        job_outlook=job_outlook,
        entry_level_education=entry_level_education,
    )


def test_lookup_bls_ooh() -> None:
    request = BlsOohRequest(
        occupation="software developer",
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
            result = lookup_bls_ooh(page, request)
            assert result.occupation == request.occupation
            print(f"\n--- Summary ---")
            print(f"  Occupation: {result.occupation}")
            print(f"  Median Pay: {result.median_pay}")
            print(f"  Job Outlook: {result.job_outlook}")
            print(f"  Entry-Level Education: {result.entry_level_education}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_lookup_bls_ooh)
