"""
Auto-generated Playwright script (Python)
Change.org – Petition Search
Query: "environmental protection"

Uses CDP-launched Chrome to avoid bot detection.
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
class PetitionSearchRequest:
    search_query: str = "environmental protection"
    max_results: int = 5


@dataclass
class Petition:
    title: str = ""
    url: str = ""
    num_signatures: str = ""
    location: str = ""
    start_date: str = ""


@dataclass
class PetitionSearchResult:
    petitions: List[Petition] = field(default_factory=list)


def change_search(page: Page, request: PetitionSearchRequest) -> PetitionSearchResult:
    """Search Change.org for petitions."""
    print(f"  Query: {request.search_query}\n")

    # ── Navigate to search results ────────────────────────────────────
    query = quote_plus(request.search_query)
    url = f"https://www.change.org/search?q={query}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Change.org search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = PetitionSearchResult()

    # ── Extract petitions from search results ─────────────────────────
    checkpoint("Extract petition list")
    js_code = r"""(maxResults) => {
        const articles = document.querySelectorAll('article');
        const items = [];
        for (const art of articles) {
            const a = art.querySelector('a[href*="/p/"]');
            if (!a) continue;
            const title = a.textContent.trim();
            const href = a.getAttribute('href') || '';
            const allText = art.innerText;
            // Signatures
            const sigMatch = allText.match(/([\d,]+)\s*sig/i);
            const sigs = sigMatch ? sigMatch[1] : '';
            // Parse lines for location and date
            const lines = allText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
            let location = '';
            let startDate = '';
            for (const line of lines) {
                if (line.match(/^Started\s/)) startDate = line.replace('Started ', '');
                // Location line: short text, not title, not signatures, not Started
                if (!location && line.match(/,/) && !line.match(/^Started/) && !line.includes('sig')
                    && line.length < 60 && line !== title.slice(0, line.length)) {
                    location = line;
                }
            }
            if (title && title.length > 5) {
                items.push({
                    title: title.slice(0, 200),
                    url: href.startsWith('http') ? href : 'https://www.change.org' + href,
                    sigs: sigs + ' signatures',
                    location,
                    startDate
                });
            }
            if (items.length >= maxResults) break;
        }
        return items;
    }"""
    petitions_data = page.evaluate(js_code, request.max_results)

    for pd in petitions_data:
        petition = Petition()
        petition.title = pd.get("title", "")
        petition.url = pd.get("url", "")
        petition.num_signatures = pd.get("sigs", "")
        petition.location = pd.get("location", "")
        petition.start_date = pd.get("startDate", "")
        result.petitions.append(petition)

    # ── Print results ─────────────────────────────────────────────────
    for i, p in enumerate(result.petitions, 1):
        print(f"\n  Petition {i}:")
        print(f"    Title:      {p.title[:80]}")
        print(f"    URL:        {p.url}")
        print(f"    Signatures: {p.num_signatures}")
        print(f"    Location:   {p.location}")
        print(f"    Started:    {p.start_date}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("change")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = PetitionSearchRequest()
            result = change_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.petitions)} petitions")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
