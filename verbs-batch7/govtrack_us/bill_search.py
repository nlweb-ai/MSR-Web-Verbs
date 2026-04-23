"""
Auto-generated Playwright script (Python)
GovTrack – Search bills about a topic

Uses CDP-launched Chrome. Navigates to the search page, collects bill links,
then visits each bill detail page to extract sponsor, status, and date.
"""

import os, sys, shutil, urllib.parse, json
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BillSearchRequest:
    search_query: str = "climate change"
    max_results: int = 5


@dataclass
class Bill:
    bill_number: str = ""
    title: str = ""
    sponsor: str = ""
    status: str = ""
    introduced_date: str = ""


@dataclass
class BillSearchResult:
    bills: List[Bill] = field(default_factory=list)


def bill_search(page: Page, request: BillSearchRequest) -> BillSearchResult:
    """Search GovTrack for bills and extract details."""
    print(f"  Query: {request.search_query}")
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Navigate to GovTrack search")
    q = urllib.parse.quote_plus(request.search_query)
    page.goto(f"https://www.govtrack.us/search?q={q}", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Collect bill links from search results")
    bill_links = page.evaluate(
        r"""(max) => {
            const results = document.querySelectorAll('#search_results_bills a[href*="/congress/bills/"]');
            const links = [];
            for (const a of results) {
                if (links.length >= max) break;
                const href = a.href;
                const text = a.textContent.trim();
                // Filter out non-bill links (like "See More")
                if (text && text.includes(':') && !text.startsWith('See')) {
                    links.push({href, text});
                }
            }
            return links;
        }""",
        request.max_results,
    )

    if not bill_links:
        # Fallback: try any link with /congress/bills/ pattern
        bill_links = page.evaluate(
            r"""(max) => {
                const results = document.querySelectorAll('a[href*="/congress/bills/"]');
                const links = [];
                for (const a of results) {
                    if (links.length >= max) break;
                    const href = a.href;
                    const text = a.textContent.trim();
                    if (text && text.includes(':') && href.match(/\/congress\/bills\/\d+\//)) {
                        links.push({href, text});
                    }
                }
                return links;
            }""",
            request.max_results,
        )

    result = BillSearchResult()

    for i, link_info in enumerate(bill_links):
        checkpoint(f"Visit bill detail page {i + 1}")
        page.goto(link_info["href"], wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        bill_data = page.evaluate(
            r"""() => {
                // Bill number and title from h1
                const h1 = document.querySelector('h1');
                let billNumber = '', title = '';
                if (h1) {
                    const fullText = h1.textContent.trim();
                    const colonIdx = fullText.indexOf(':');
                    if (colonIdx > 0) {
                        billNumber = fullText.slice(0, colonIdx).trim();
                        title = fullText.slice(colonIdx + 1).trim();
                    } else {
                        title = fullText;
                    }
                }

                // Sponsor from the first link near "Sponsor" text
                let sponsor = '';
                const bodyText = document.body.innerText;
                // Look for the sponsor paragraph - usually first <p> or near "Sponsor"
                const allPs = document.querySelectorAll('p');
                for (const p of allPs) {
                    const t = p.textContent.trim();
                    if (t.includes('Sponsor.') || t.includes('Senator for') || t.includes('Representative for')) {
                        // Get the previous sibling or nearby element with sponsor name
                        const prev = p.previousElementSibling;
                        if (prev) {
                            const link = prev.querySelector('a');
                            sponsor = link ? link.textContent.trim() : prev.textContent.trim();
                        }
                        break;
                    }
                }
                if (!sponsor) {
                    // Try finding by looking for name near "Sponsor"
                    const sponsorMatch = bodyText.match(/Sponsor\.\s*(?:Senior\s+)?(?:Senator|Representative)\s+for\s+[\w\s']+\.\s*(Democrat|Republican)/);
                    // Or just get the first bold/heading near "Sponsor"
                }

                // Introduced date
                let introduced = '';
                const dateMatch = bodyText.match(/Introduced\s+(?:on\s+)?(\w+ \d{1,2}, \d{4})/);
                if (dateMatch) introduced = dateMatch[1];

                // Status
                let status = '';
                const statusMatch = bodyText.match(/Status\s*\n+(.*?)(?:\n|$)/);
                if (statusMatch) status = statusMatch[1].trim();
                if (!status) {
                    const statusMatch2 = bodyText.match(/Introduced on (\w+ \d{1,2}, \d{4})/);
                    if (statusMatch2) status = 'Introduced';
                }

                return {billNumber, title, sponsor, status, introduced};
            }"""
        )

        b = Bill()
        b.bill_number = bill_data.get("billNumber", "")
        b.title = bill_data.get("title", "")
        b.sponsor = bill_data.get("sponsor", "")
        b.status = bill_data.get("status", "Introduced")
        b.introduced_date = bill_data.get("introduced", "")
        result.bills.append(b)

    for i, b in enumerate(result.bills):
        print(f"  Bill {i + 1}:")
        print(f"    Number:    {b.bill_number}")
        print(f"    Title:     {b.title}")
        print(f"    Sponsor:   {b.sponsor}")
        print(f"    Status:    {b.status}")
        print(f"    Introduced: {b.introduced_date}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("govtrack")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = BillSearchRequest()
            result = bill_search(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.bills)} bills")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
