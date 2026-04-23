"""
Auto-generated Playwright script (Python)
Statista – Statistics Search

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
class SearchRequest:
    search_query: str = "global smartphone market share"
    max_results: int = 5


@dataclass
class StatResult:
    title: str = ""
    description: str = ""
    region: str = ""
    time_period: str = ""


@dataclass
class SearchResult:
    stats: List[StatResult] = field(default_factory=list)


def statista_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search Statista for statistics."""
    print(f"  Query: {request.search_query}\n")

    query_encoded = request.search_query.replace(" ", "+")
    url = f"https://www.statista.com/search/?q={query_encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = SearchResult()

    checkpoint("Extract search results")
    js_code = r"""(max) => {
        const body = document.body.innerText;
        const lines = body.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find "results found" line
        let startIdx = 0;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].match(/\d+\s+results found/)) {
                startIdx = i + 2; // skip "Search results"
                break;
            }
        }
        const stats = [];
        let i = startIdx;
        while (i < lines.length && stats.length < max) {
            let line = lines[i];
            // Skip "Premium Statistic" or "Free Statistic" labels
            if (line === 'Premium Statistic' || line === 'Free Statistic') {
                i++; continue;
            }
            // Title line
            const title = line;
            i++;
            if (i >= lines.length) break;
            // Description (may be multi-paragraph, collect until we hit region line)
            let desc = '';
            while (i < lines.length) {
                const l = lines[i];
                // Region line is like "Worldwide" or "United States"
                if (/^(Worldwide|United States|Europe|Asia|China|India|North America)/.test(l)) break;
                desc += (desc ? ' ' : '') + l;
                i++;
            }
            if (i >= lines.length) break;
            const region = lines[i];
            i++;
            if (i >= lines.length) break;
            const timePeriod = lines[i];
            i++;
            // Skip "Source information"
            if (i < lines.length && lines[i] === 'Source information') i++;
            if (title && !title.startsWith("Didn't find")) {
                stats.push({title, description: desc.slice(0, 200), region, time_period: timePeriod});
            }
        }
        return stats;
    }"""
    stats_data = page.evaluate(js_code, request.max_results)

    for sd in stats_data:
        s = StatResult()
        s.title = sd.get("title", "")
        s.description = sd.get("description", "")
        s.region = sd.get("region", "")
        s.time_period = sd.get("time_period", "")
        result.stats.append(s)

    for i, s in enumerate(result.stats, 1):
        print(f"\n  Stat {i}:")
        print(f"    Title:   {s.title}")
        print(f"    Region:  {s.region}")
        print(f"    Period:  {s.time_period}")
        print(f"    Summary: {s.description[:100]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("statista")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = statista_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.stats)} stats")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
