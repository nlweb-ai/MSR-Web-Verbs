"""
Auto-generated Playwright script (Python)
Mountain Project – Route Search
Query: "Yosemite trad climbing"
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
class RouteRequest:
    query: str = "Yosemite trad climbing"
    max_results: int = 5


@dataclass
class Route:
    name: str = ""
    grade: str = ""
    location: str = ""
    url: str = ""


@dataclass
class RouteResult:
    routes: List[Route] = field(default_factory=list)


def mountainproject_search(page: Page, request: RouteRequest) -> RouteResult:
    """Search Mountain Project for climbing routes."""
    print(f"  Query: {request.query}\n")

    from urllib.parse import quote_plus
    url = f"https://www.mountainproject.com/search?q={quote_plus(request.query)}&type=route"
    print(f"Loading {url}...")
    checkpoint("Navigate to Mountain Project search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract route listings")
    routes_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();

        // Look for route links: /route/{id}/{slug}
        const links = document.querySelectorAll('a[href*="/route/"]');
        for (const a of links) {
            if (results.length >= maxResults) break;
            const href = a.getAttribute('href') || '';
            if (!/\/route\/\d+/.test(href)) continue;

            const block = a.closest('tr, li, div') || a;
            const text = block.innerText || '';
            const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 1);

            let name = a.innerText.trim().split('\n')[0].trim();
            if (!name || name.length < 3 || seen.has(name)) continue;
            if (/^(search|home|sign|log|menu)/i.test(name)) continue;
            seen.add(name);

            let grade = '', location = '';
            for (const line of lines) {
                if (!grade && /^5\.\d|^V\d|^WI\d/i.test(line)) grade = line.split(' ')[0];
                if (!grade) { const gm = line.match(/(5\.\d+[a-d]?[+-]?|V\d+[+-]?)/); if (gm) grade = gm[1]; }
                if (!location && /,/.test(line) && line.length > 10 && line.length < 80) location = line;
            }

            const fullUrl = href.startsWith('/') ? 'https://www.mountainproject.com' + href : href;
            results.push({ name: name.slice(0, 100), grade, location: location.slice(0, 80), url: fullUrl });
        }

        // Fallback: scan body text
        if (results.length === 0) {
            const text = document.body.innerText;
            const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 10 && l.length < 120);
            for (const line of lines) {
                if (results.length >= maxResults) break;
                if (/climb|route|trad|sport|boulder/i.test(line) && !seen.has(line)) {
                    seen.add(line);
                    results.push({ name: line.slice(0, 100), grade: '', location: '', url: '' });
                }
            }
        }
        return results;
    }""", request.max_results)

    routes = [Route(**d) for d in routes_data]
    result = RouteResult(routes=routes[:request.max_results])

    print("\n" + "=" * 60)
    print(f"Mountain Project: {request.query}")
    print("=" * 60)
    for i, r in enumerate(result.routes, 1):
        print(f"  {i}. {r.name}")
        if r.grade:
            print(f"     Grade:    {r.grade}")
        if r.location:
            print(f"     Location: {r.location}")
        if r.url:
            print(f"     URL:      {r.url}")
    print(f"\nTotal: {len(result.routes)} routes")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("mountainproject_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = mountainproject_search(page, RouteRequest())
            print(f"\nReturned {len(result.routes)} routes")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
