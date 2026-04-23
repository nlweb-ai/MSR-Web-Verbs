"""
Auto-generated Playwright script (Python)
payscale.com – Salary Data
Job title: "Data Scientist"

Generated on: 2026-04-18T01:56:22.194Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class PayScaleRequest:
    job_title: str = "Data Scientist"
    job_slug: str = "Data_Scientist"


@dataclass(frozen=True)
class PayScaleResult:
    average_salary: str = ""
    salary_range_low: str = ""
    salary_range_high: str = ""
    bonus_range: str = ""
    total_pay_range: str = ""
    num_profiles: str = ""
    experience_levels: list = None  # list of dicts


def payscale_salary(page: Page, request: PayScaleRequest) -> PayScaleResult:
    """Extract salary data from PayScale."""
    print(f"  Job title: {request.job_title}\n")

    # ── Navigate ──────────────────────────────────────────────────────
    url = f"https://www.payscale.com/research/US/Job={request.job_slug}/Salary"
    print(f"Loading {url}...")
    checkpoint("Navigate to PayScale salary page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Extract salary data from page text ────────────────────────────
    data = page.evaluate(r"""() => {
        const text = document.body.innerText;

        // Average salary: "$103,382 / year" pattern
        const avgMatch = text.match(/(\$[\d,]+)\s*\/\s*year\s*\n\s*Avg/);
        const avgSalary = avgMatch ? avgMatch[1] : '';

        // Salary range from "Base Salary" line
        const baseMatch = text.match(/Base Salary\s*\n\s*(\$\w+)\s*-\s*(\$\w+)/);
        const rangeLow = baseMatch ? baseMatch[1] : '';
        const rangeHigh = baseMatch ? baseMatch[2] : '';

        // Bonus range
        const bonusMatch = text.match(/Bonus\s*\n\s*(\$\w+)\s*-\s*(\$\w+)/);
        const bonus = bonusMatch ? bonusMatch[1] + ' - ' + bonusMatch[2] : '';

        // Total pay range
        const totalMatch = text.match(/Total Pay\s*\n\s*(\$\w+)\s*-\s*(\$\w+)/);
        const totalPay = totalMatch ? totalMatch[1] + ' - ' + totalMatch[2] : '';

        // Number of profiles
        const profileMatch = text.match(/Based on ([\d,]+) salary profiles/);
        const numProfiles = profileMatch ? profileMatch[1] : '';

        // Experience levels
        const levels = [];
        const expPattern = /(Entry Level|Early Career|Mid Career|Late Career|Experienced)\s*\n\s*([▲▼])([\d]+)%/g;
        let m;
        while ((m = expPattern.exec(text)) !== null) {
            levels.push({
                level: m[1],
                direction: m[2] === '▲' ? '+' : '-',
                percent: m[3] + '%',
            });
        }

        return { avgSalary, rangeLow, rangeHigh, bonus, totalPay, numProfiles, levels };
    }""")

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"PayScale Salary Data: {request.job_title}")
    print("=" * 60)
    print(f"\n  Average Salary: {data['avgSalary']}")
    print(f"  Salary Range: {data['rangeLow']} - {data['rangeHigh']}")
    print(f"  Bonus Range: {data['bonus']}")
    print(f"  Total Pay Range: {data['totalPay']}")
    print(f"  Based on: {data['numProfiles']} salary profiles")

    if data['levels']:
        print("\n  Pay by Experience Level:")
        for lvl in data['levels']:
            print(f"    {lvl['level']}: {lvl['direction']}{lvl['percent']}")

    return PayScaleResult(
        average_salary=data['avgSalary'],
        salary_range_low=data['rangeLow'],
        salary_range_high=data['rangeHigh'],
        bonus_range=data['bonus'],
        total_pay_range=data['totalPay'],
        num_profiles=data['numProfiles'],
        experience_levels=data['levels'],
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("payscale_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = payscale_salary(page, PayScaleRequest())
            print(f"\nResult: {result.average_salary}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
