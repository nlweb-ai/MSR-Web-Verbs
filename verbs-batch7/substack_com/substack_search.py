"""
Auto-generated Playwright script (Python)
Substack – Newsletter Search

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
    search_query: str = "artificial intelligence"
    max_results: int = 5


@dataclass
class NewsletterResult:
    name: str = ""
    handle: str = ""
    description: str = ""


@dataclass
class SearchResult:
    newsletters: List[NewsletterResult] = field(default_factory=list)


def substack_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search Substack for newsletters."""
    print(f"  Query: {request.search_query}\n")

    query_encoded = request.search_query.replace(" ", "%20")
    url = f"https://substack.com/search/{query_encoded}?type=publications"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = SearchResult()

    checkpoint("Extract newsletter results")
    js_code = r"""(max) => {
        const body = document.body.innerText;
        const lines = body.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        // Publications are at the top: Name, @handle · Description, description, "Follow"
        const newsletters = [];
        let i = 0;
        // Skip navigation tabs
        for (; i < lines.length; i++) {
            if (lines[i] === 'People') { i++; break; }
        }
        while (i < lines.length && newsletters.length < max) {
            const name = lines[i];
            // End when we hit post-like content (dates, like "Apr 23, 2024")
            if (/^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d/.test(name)) break;
            if (name === 'Follow') { i++; continue; }
            // Check if next line has @handle pattern
            if (i + 1 < lines.length && lines[i + 1].includes('@')) {
                const handleLine = lines[i + 1];
                const handleMatch = handleLine.match(/@(\w+)/);
                const handle = handleMatch ? '@' + handleMatch[1] : '';
                // Publication name from handle line (after ∙)
                const pubName = handleLine.includes('∙') ? handleLine.split('∙')[1].trim() : '';
                i += 2;
                // Description line
                let desc = '';
                if (i < lines.length && lines[i] !== 'Follow') {
                    desc = lines[i];
                    i++;
                }
                // Skip "Follow"
                if (i < lines.length && lines[i] === 'Follow') i++;
                newsletters.push({name, handle, description: desc});
            } else {
                i++;
            }
        }
        return newsletters;
    }"""
    newsletters_data = page.evaluate(js_code, request.max_results)

    for nd in newsletters_data:
        n = NewsletterResult()
        n.name = nd.get("name", "")
        n.handle = nd.get("handle", "")
        n.description = nd.get("description", "")
        result.newsletters.append(n)

    for i, n in enumerate(result.newsletters, 1):
        print(f"\n  Newsletter {i}:")
        print(f"    Name:        {n.name}")
        print(f"    Handle:      {n.handle}")
        print(f"    Description: {n.description[:100]}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("substack")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = substack_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.newsletters)} newsletters")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
