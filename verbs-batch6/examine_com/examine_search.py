"""
Auto-generated Playwright script (Python)
Examine.com – Supplement Information
Supplement: "creatine"

Generated on: 2026-04-18T05:18:29.038Z
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
class SupplementRequest:
    supplement: str = "creatine"


@dataclass
class SupplementResult:
    name: str = ""
    benefits: str = ""
    evidence_grade: str = ""
    dosage: str = ""
    findings: str = ""


def examine_search(page: Page, request: SupplementRequest) -> SupplementResult:
    """Look up supplement info on Examine.com."""
    print(f"  Supplement: {request.supplement}\n")

    # ── Step 1: Navigate to the supplement page ───────────────────────
    url = f"https://examine.com/supplements/{quote_plus(request.supplement.lower())}/"
    print(f"Loading {url}...")
    checkpoint("Navigate to Examine supplement page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Step 2: Extract supplement data ───────────────────────────────
    checkpoint("Extract supplement data")
    data = page.evaluate(r"""() => {
        const text = document.body.innerText;
        const result = {};

        // Supplement name
        const h1 = document.querySelector('h1');
        result.name = h1 ? h1.innerText.trim() : '';

        // Summary/description - first substantial paragraph
        const paragraphs = document.querySelectorAll('p');
        for (const p of paragraphs) {
            const t = p.innerText.trim();
            if (t.length > 50 && !t.includes('Cookie') && !t.includes('privacy')) {
                result.summary = t.slice(0, 500);
                break;
            }
        }

        // Evidence grades - look for grade letters with outcomes
        const grades = [];
        const gradeRegex = /([A-D])\n([^\n]+)/g;
        let match;
        const researchSection = text.slice(text.indexOf('Research Snapshot'), text.indexOf('Overview') > 0 ? text.indexOf('Overview') : text.length);
        while ((match = gradeRegex.exec(researchSection)) !== null && grades.length < 5) {
            grades.push({ grade: match[1], outcome: match[2].trim() });
        }
        result.evidence_grades = grades;

        // Dosage
        const dosageIdx = text.indexOf('Dosage Information');
        if (dosageIdx >= 0) {
            // Look for dosage text following the header
            const dosageSection = text.slice(dosageIdx, dosageIdx + 800);
            // Find first line with grams or mg
            const dosageMatch = dosageSection.match(/(\d+[\d.]*\s*(?:g|mg|grams|milligrams)[^\n]*)/i);
            result.dosage = dosageMatch ? dosageMatch[0].trim() : '';
        }
        // Also look in the main text for dosage info
        if (!result.dosage) {
            const doseMatch = text.match(/(?:loading|maintenance)\s+(?:dose|protocol)[^.]*?(\d+[\d.]*\s*(?:g|mg)\/?\w*[^.]*\.)/i);
            if (doseMatch) result.dosage = doseMatch[0].trim().slice(0, 200);
        }
        // Simpler: look for the "3-5 g" daily dose
        if (!result.dosage) {
            const simpleMatch = text.match(/(\d+[-–]\d+\s*g(?:rams)?)\s*(?:of\s+\w+\s+)?(?:every|per|daily|a)\s+day/i);
            if (simpleMatch) result.dosage = simpleMatch[0].trim();
        }

        // Key benefits from the overview/summary
        const benefitsMatch = text.match(/main benefits\?[\s\S]*?(?=What are|How does|Dosage)/i);
        if (benefitsMatch) {
            result.benefits = benefitsMatch[0].replace(/main benefits\?\s*/i, '').trim().slice(0, 300);
        }

        return result;
    }""")

    result = SupplementResult(
        name=data.get("name", request.supplement.title()),
        benefits=data.get("benefits", ""),
        evidence_grade=", ".join(f"{g['grade']}: {g['outcome']}" for g in data.get("evidence_grades", [])),
        dosage=data.get("dosage", ""),
        findings=data.get("summary", ""),
    )

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Examine: {result.name}")
    print("=" * 60)
    print(f"\n  Summary:")
    print(f"  {result.findings}")
    if data.get("evidence_grades"):
        print(f"\n  Evidence Grades:")
        for g in data["evidence_grades"]:
            print(f"    {g['grade']}: {g['outcome']}")
    if result.dosage:
        print(f"\n  Dosage: {result.dosage}")
    if result.benefits:
        print(f"\n  Benefits: {result.benefits}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("examine_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = examine_search(page, SupplementRequest())
            print(f"\nReturned info for {result.name}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
