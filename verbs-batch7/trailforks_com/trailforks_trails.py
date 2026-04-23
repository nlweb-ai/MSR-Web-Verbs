"""
Auto-generated Playwright script (Python)
Trailforks – Mountain Bike Trails

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
class TrailRequest:
    region: str = "moab"
    max_results: int = 5


@dataclass
class TrailResult:
    name: str = ""
    riding_area: str = ""
    distance: str = ""
    descent: str = ""
    climb: str = ""


@dataclass
class TrailsResult:
    trails: List[TrailResult] = field(default_factory=list)


def trailforks_trails(page: Page, request: TrailRequest) -> TrailsResult:
    """List mountain bike trails from Trailforks."""
    print(f"  Region: {request.region}\n")

    url = f"https://www.trailforks.com/region/{request.region}/trails/"
    print(f"Loading {url}...")
    checkpoint("Navigate to trails page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = TrailsResult()

    checkpoint("Extract trail data")
    js_code = r"""(max) => {
        const body = document.body.innerText;
        const lines = body.split('\n');
        // Find start after "climb" header
        let startIdx = 0;
        for (let i = 0; i < lines.length; i++) {
            const parts = lines[i].split('\t').map(s => s.trim()).filter(s => s);
            if (parts.length === 1 && parts[0] === 'climb') { startIdx = i + 1; break; }
        }
        const trails = [];
        let i = startIdx;
        while (i < lines.length - 1 && trails.length < max) {
            const nameParts = lines[i].split('\t').map(s => s.trim()).filter(s => s);
            i++;
            if (nameParts.length < 1) continue;
            // Skip empty lines
            if (nameParts.length === 0) continue;
            const dataParts = lines[i].split('\t').map(s => s.trim()).filter(s => s);
            i++;
            // nameParts: [trailName, ridingArea]
            // dataParts: [distance, descent, climb] (climb may be missing)
            const name = nameParts[0] || '';
            const riding_area = nameParts[1] || '';
            if (!name || /^Showing|^Page|^←|^→/.test(name)) break;
            const distance = dataParts[0] || '';
            const descent = dataParts[1] || '';
            const climb = dataParts[2] || '';
            trails.push({name, riding_area, distance, descent, climb});
        }
        return trails;
    }"""
    trails_data = page.evaluate(js_code, request.max_results)

    for td in trails_data:
        t = TrailResult()
        t.name = td.get("name", "")
        t.riding_area = td.get("riding_area", "")
        t.distance = td.get("distance", "")
        t.descent = td.get("descent", "")
        t.climb = td.get("climb", "")
        result.trails.append(t)

    for i, t in enumerate(result.trails, 1):
        print(f"\n  Trail {i}:")
        print(f"    Name:     {t.name}")
        print(f"    Area:     {t.riding_area}")
        print(f"    Distance: {t.distance}")
        print(f"    Descent:  {t.descent}")
        print(f"    Climb:    {t.climb}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("trailforks")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = TrailRequest()
            result = trailforks_trails(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.trails)} trails")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
