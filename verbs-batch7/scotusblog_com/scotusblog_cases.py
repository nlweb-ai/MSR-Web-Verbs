"""
Auto-generated Playwright script (Python)
SCOTUSblog – Case Files Browser

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CaseRequest:
    term: str = "ot2025"
    max_cases: int = 5


@dataclass
class Case:
    case_name: str = ""
    docket_number: str = ""
    issue: str = ""
    status: str = ""


@dataclass
class CaseResult:
    cases: List[Case] = field(default_factory=list)


def scotusblog_cases(page: Page, request: CaseRequest) -> CaseResult:
    """Browse SCOTUSblog for recent Supreme Court cases."""
    print(f"  Term: {request.term}\n")

    # ── Navigate to term page ─────────────────────────────────────────
    url = f"https://www.scotusblog.com/case-files/terms/{request.term}/"
    print(f"Loading {url}...")
    checkpoint("Navigate to SCOTUSblog")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = CaseResult()

    # ── Extract cases via text parsing ────────────────────────────────
    checkpoint("Extract case entries")
    js_code = r"""(max) => {
        const body = document.body.innerText;
        // Match case entries: NAME No. XX-XXXX [Arg: ... ; Decided MM.DD.YYYY]
        // or cases with Issue(s):
        const caseRegex = /([A-Z][A-Z\s.,''()\/]+?)\s+No\.\s+([\d-]+)\s+\[([^\]]+)\]\s*\n((?:Holding|Issue\(s\)):[\s\S]*?)(?=\n(?:Case Preview|[A-Z][A-Z\s.,''()\/]+?\s+No\.))/g;
        const cases = [];
        let match;
        while ((match = caseRegex.exec(body)) !== null && cases.length < max) {
            const caseName = match[1].trim();
            const docket = 'No. ' + match[2].trim();
            const bracketInfo = match[3].trim();
            const holdingText = match[4].trim();

            // Extract status from bracket info
            let status = 'Pending';
            const decidedMatch = bracketInfo.match(/Decided\s+([\d.]+)/);
            if (decidedMatch) {
                status = 'Decided ' + decidedMatch[1];
            }

            // Clean holding/issue text
            let issue = holdingText
                .replace(/^(Holding|Issue\(s\)):\s*/, '')
                .replace(/\n/g, ' ')
                .trim();
            // Truncate if too long
            if (issue.length > 300) issue = issue.substring(0, 297) + '...';

            cases.push({caseName, docket, issue, status});
        }
        return cases;
    }"""
    cases_data = page.evaluate(js_code, request.max_cases)

    for cd in cases_data:
        case = Case()
        case.case_name = cd.get("caseName", "")
        case.docket_number = cd.get("docket", "")
        case.issue = cd.get("issue", "")
        case.status = cd.get("status", "")
        result.cases.append(case)

    # ── Print results ─────────────────────────────────────────────────
    for i, c in enumerate(result.cases, 1):
        print(f"\n  Case {i}:")
        print(f"    Name:    {c.case_name}")
        print(f"    Docket:  {c.docket_number}")
        print(f"    Status:  {c.status}")
        print(f"    Issue:   {c.issue[:150]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("scotusblog")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = CaseRequest()
            result = scotusblog_cases(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.cases)} cases")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
