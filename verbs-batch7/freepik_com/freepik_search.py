"""
Auto-generated Playwright script (Python)
Freepik – Search for design resources

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, urllib.parse
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class FreepikRequest:
    search_query: str = "business infographic template"
    max_results: int = 5


@dataclass
class Resource:
    title: str = ""
    url: str = ""
    resource_type: str = ""
    is_premium: bool = False


@dataclass
class FreepikResult:
    resources: List[Resource] = field(default_factory=list)


def freepik_search(page: Page, request: FreepikRequest) -> FreepikResult:
    """Search Freepik and extract resource results."""
    print(f"  Query: {request.search_query}")
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Navigate to Freepik search")
    q = urllib.parse.quote_plus(request.search_query)
    page.goto(f"https://www.freepik.com/search?format=search&query={q}", wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    checkpoint("Extract resource cards")
    result = FreepikResult()

    items = page.evaluate(
        r"""(max) => {
            const figures = document.querySelectorAll('figure[data-cy="resource-thumbnail"]');
            const results = [];
            for (let i = 0; i < figures.length && results.length < max; i++) {
                const fig = figures[i];
                const link = fig.querySelector('a');
                const href = link ? link.href : '';
                const img = fig.querySelector('img');
                const alt = img ? img.alt : '';
                let type = 'unknown';
                if (href.includes('/free-vector/') || href.includes('/premium-vector/')) type = 'Vector';
                else if (href.includes('/free-psd/') || href.includes('/premium-psd/')) type = 'PSD';
                else if (href.includes('/free-photo/') || href.includes('/premium-photo/')) type = 'Photo';
                const isPremium = href.includes('/premium-');
                results.push({title: alt, url: href.split('#')[0], type: type, is_premium: isPremium});
            }
            return results;
        }""",
        request.max_results,
    )

    for item in items:
        r = Resource()
        r.title = item.get("title", "")
        r.url = item.get("url", "")
        r.resource_type = item.get("type", "")
        r.is_premium = item.get("is_premium", False)
        result.resources.append(r)

    print(f"Loading https://www.freepik.com/search?format=search&query={q}...\n")
    for i, r in enumerate(result.resources):
        print(f"  Resource {i + 1}:")
        print(f"    Title:    {r.title}")
        print(f"    Type:     {r.resource_type}")
        print(f"    Premium:  {r.is_premium}")
        print(f"    URL:      {r.url}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("freepik")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = FreepikRequest()
            result = freepik_search(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.resources)} resources")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
