"""
Playwright script (Python) — Mayo Clinic Condition Search
Search Mayo Clinic for a condition and extract medical information.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MayoClinicRequest:
    query: str = "high blood pressure"


@dataclass
class ConditionInfo:
    condition_name: str = ""
    definition: str = ""
    symptoms: str = ""
    causes: str = ""
    risk_factors: str = ""
    when_to_see_doctor: str = ""


@dataclass
class MayoClinicResult:
    info: ConditionInfo = field(default_factory=ConditionInfo)


# Searches Mayo Clinic for a condition and extracts name, definition,
# symptoms, causes, risk factors, and when to see a doctor.
def search_mayoclinic(page: Page, request: MayoClinicRequest) -> MayoClinicResult:
    url = f"https://www.mayoclinic.org/search/search-results?q={request.query.replace(' ', '+')}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Mayo Clinic search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)

    checkpoint("Click first search result")
    # Scroll down to search results area first
    page.evaluate("window.scrollBy(0, 400)")
    page.wait_for_timeout(1000)
    first_link = page.query_selector(".azsearchresult a, .result a, #main-content .content a, ol a, ul.result-list a")
    if first_link:
        first_link.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        first_link.click()
        page.wait_for_timeout(5000)
    else:
        # Try direct condition page
        page.goto("https://www.mayoclinic.org/diseases-conditions/high-blood-pressure/symptoms-causes/syc-20373410",
                   wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)

    result = MayoClinicResult()
    info = ConditionInfo()

    checkpoint("Extract condition information")
    js_code = """() => {
        const title = document.querySelector('h1, .content-title');
        const name = title ? title.textContent.trim() : '';
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);

        function extractSection(heading) {
            let startIdx = -1;
            // Find ALL occurrences, use the last one that has real content after it
            for (let i = lines.length - 1; i >= 0; i--) {
                if (lines[i].toLowerCase() === heading.toLowerCase()) {
                    for (let k = i + 1; k < Math.min(i + 6, lines.length); k++) {
                        if (lines[k].length > 30) {
                            startIdx = k;
                            break;
                        }
                    }
                    if (startIdx >= 0) break;
                }
            }
            if (startIdx < 0) return '';
            const sectionHeaders = ['Overview', 'Symptoms', 'Causes', 'Risk factors', 'Complications', 'Prevention', 'When to see a doctor', 'Products & Services', 'Request an appointment', 'More Information'];
            let text = '';
            for (let j = startIdx; j < lines.length && text.length < 500; j++) {
                if (sectionHeaders.includes(lines[j]) && j > startIdx) break;
                if (/^Products & Services$/i.test(lines[j])) break;
                text += lines[j] + ' ';
            }
            return text.trim();
        }

        return {
            condition_name: name,
            definition: extractSection('Overview'),
            symptoms: extractSection('Symptoms'),
            causes: extractSection('Causes'),
            risk_factors: extractSection('Risk factors'),
            when_to_see_doctor: extractSection('When to see a doctor'),
        };
    }"""
    data = page.evaluate(js_code)

    info.condition_name = data.get("condition_name", "")
    info.definition = data.get("definition", "")
    info.symptoms = data.get("symptoms", "")
    info.causes = data.get("causes", "")
    info.risk_factors = data.get("risk_factors", "")
    info.when_to_see_doctor = data.get("when_to_see_doctor", "")
    result.info = info

    print(f"\nCondition: {info.condition_name}")
    print(f"Definition: {info.definition[:200]}...")
    print(f"Symptoms: {info.symptoms[:200]}...")
    print(f"Causes: {info.causes[:200]}...")
    print(f"Risk Factors: {info.risk_factors[:200]}...")
    print(f"When to see doctor: {info.when_to_see_doctor[:200]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("mayoclinic")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_mayoclinic(page, MayoClinicRequest())
            print("\n=== DONE ===")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
