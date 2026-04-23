"""
Auto-generated Playwright script (Python)
Justia – Legal Case Search
Query: "employment discrimination"

Generated on: 2026-04-18T14:45:23.886Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CaseRequest:
    query: str = "employment discrimination"
    max_results: int = 5


@dataclass
class LegalCase:
    name: str = ""
    court: str = ""
    date: str = ""
    summary: str = ""


@dataclass
class CaseResult:
    cases: List[LegalCase] = field(default_factory=list)


def justia_search(page: Page, request: CaseRequest) -> CaseResult:
    """Search Justia for employment discrimination cases."""
    print(f"  Query: {request.query}\n")

    # ── Step 1: Navigate to Justia labor & employment cases page ──────
    url = "https://supreme.justia.com/cases-by-topic/labor-employment/"
    print("Loading Justia Supreme Court labor & employment cases...")
    checkpoint("Navigate to Justia cases page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # ── Step 2: Extract case entries ────────────────────────────────────
    checkpoint("Extract case listings")
    items = page.evaluate(r"""(maxResults) => {
        const text = document.body.innerText;
        const results = [];

        // Get case links for the names
        const caseLinks = document.querySelectorAll('a[href*="/cases/federal/us/"]');
        const caseNames = [];
        const seen = new Set();
        for (const link of caseLinks) {
            const name = link.innerText.trim();
            if (name && name.includes('v.') && !seen.has(name)) {
                seen.add(name);
                caseNames.push(name);
            }
        }

        // For each case name, find its block in the text
        for (let i = 0; i < caseNames.length && results.length < maxResults; i++) {
            const name = caseNames[i];
            const idx = text.indexOf(name);
            if (idx < 0) continue;

            // Get text from this case name to the next case name (or end)
            const nextIdx = (i + 1 < caseNames.length) ? text.indexOf(caseNames[i + 1], idx + name.length) : text.length;
            const block = text.slice(idx, nextIdx > idx ? nextIdx : text.length);

            // Extract year
            const yearMatch = block.match(/\((\d{4})\)/);
            const year = yearMatch ? yearMatch[1] : '';

            // Extract summary (after "Author: ...\n\n")
            const summaryMatch = block.match(/Author:[^\n]+\n\s*\n([^\n]+)/);
            const summary = summaryMatch ? summaryMatch[1].trim() : '';

            results.push({ name, court: 'U.S. Supreme Court', date: year, summary: summary.slice(0, 300) });
        }
        return results;
    }""", request.max_results)

    result = CaseResult(cases=[LegalCase(
        name=c['name'], court=c['court'], date=c['date'], summary=c['summary']
    ) for c in items])

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(f"Justia: Employment Discrimination Cases")
    print("=" * 70)
    for i, c in enumerate(items, 1):
        print(f"\n  {i}. {c['name']} ({c['date']})")
        print(f"     Court: {c['court']}")
        print(f"     {c['summary']}")
    print(f"\n  Total: {len(items)} cases")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("justia_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = justia_search(page, CaseRequest())
            print(f"\nReturned {len(result.cases)} cases")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
