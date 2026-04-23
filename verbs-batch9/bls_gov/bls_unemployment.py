"""
Playwright script (Python) — BLS Unemployment Data
Search Bureau of Labor Statistics for unemployment data.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BLSUnemploymentRequest:
    query: str = "unemployment rate"
    max_results: int = 5


@dataclass
class LaborStatItem:
    group: str = ""
    rate: str = ""


@dataclass
class BLSUnemploymentResult:
    current_rate: str = ""
    statistics: List[LaborStatItem] = field(default_factory=list)


def get_bls_unemployment(page: Page, request: BLSUnemploymentRequest) -> BLSUnemploymentResult:
    """Get unemployment data from BLS."""
    url = "https://www.bls.gov/cps/"
    print(f"Loading {url}...")
    checkpoint("Navigate to BLS CPS page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = BLSUnemploymentResult()

    checkpoint("Extract unemployment data")
    js_code = """() => {
        const items = [];
        let current = '';
        // Find Latest Numbers section
        const h2s = document.querySelectorAll('h2');
        for (const h of h2s) {
            if (h.textContent.includes('Latest')) {
                const section = h.parentElement;
                const lines = section.innerText.split('\\n').map(l => l.trim()).filter(l => l);
                for (let i = 0; i < lines.length; i++) {
                    const label = lines[i].replace(/:$/, '').trim();
                    if (i + 1 < lines.length) {
                        const val = lines[i+1].match(/^(\\d+\\.\\d+%?)$/);
                        if (val) {
                            let period = '';
                            if (i + 2 < lines.length) {
                                const pm = lines[i+2].match(/^in\\s+(.+)/);
                                if (pm) period = pm[1];
                            }
                            const rate = val[1];
                            if (label.match(/Unemployment Rate/i) && !current) current = rate;
                            items.push({group: label, rate: rate + (period ? ' (' + period + ')' : '')});
                        }
                    }
                }
                break;
            }
        }
        return {current_rate: current, items: items};
    }"""
    data = page.evaluate(js_code)

    result.current_rate = data.get("current_rate", "")
    for d in data.get("items", [])[:request.max_results]:
        item = LaborStatItem()
        item.group = d.get("group", "")
        item.rate = d.get("rate", "")
        result.statistics.append(item)

    print(f"\nCurrent unemployment rate: {result.current_rate}")
    print(f"Statistics ({len(result.statistics)}):")
    for i, item in enumerate(result.statistics, 1):
        print(f"  {i}. {item.group}: {item.rate}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("bls")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = get_bls_unemployment(page, BLSUnemploymentRequest())
            print("\n=== DONE ===")
            print(f"Current rate: {result.current_rate}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
