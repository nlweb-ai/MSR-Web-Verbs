"""
FEC.gov – Search for campaign finance data by candidate name or keyword

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class FecSearchRequest:
    search_query: str = "president"
    max_results: int = 5


@dataclass
class FecCandidateItem:
    candidate_name: str = ""
    party: str = ""
    office: str = ""
    state: str = ""
    total_receipts: str = ""
    total_disbursements: str = ""
    cash_on_hand: str = ""
    election_year: str = ""


@dataclass
class FecSearchResult:
    items: List[FecCandidateItem] = field(default_factory=list)


# Search for campaign finance data on FEC.gov by candidate name or keyword.
def fec_search(page: Page, request: FecSearchRequest) -> FecSearchResult:
    """Search for campaign finance data on FEC.gov."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://www.fec.gov/data/candidates/?search={query}"
    print(f"Loading {url}...")
    checkpoint("Navigate to FEC.gov candidate search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = FecSearchResult()

    checkpoint("Extract candidate finance listings")
    js_code = """(max) => {
        const rows = document.querySelectorAll('table tbody tr, .data-table tbody tr, [class*="candidate"] tr');
        const items = [];
        for (const row of rows) {
            if (items.length >= max) break;
            const cells = row.querySelectorAll('td');
            const nameEl = row.querySelector('a, td:first-child');
            const candidate_name = nameEl ? nameEl.textContent.trim() : '';
            if (!candidate_name) continue;

            const party = cells[1] ? cells[1].textContent.trim() : '';
            const office = cells[2] ? cells[2].textContent.trim() : '';
            const state = cells[3] ? cells[3].textContent.trim() : '';
            const total_receipts = cells[4] ? cells[4].textContent.trim() : '';
            const total_disbursements = cells[5] ? cells[5].textContent.trim() : '';
            const cash_on_hand = cells[6] ? cells[6].textContent.trim() : '';
            const election_year = cells[7] ? cells[7].textContent.trim() : '';

            items.push({candidate_name, party, office, state, total_receipts, total_disbursements, cash_on_hand, election_year});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = FecCandidateItem()
        item.candidate_name = d.get("candidate_name", "")
        item.party = d.get("party", "")
        item.office = d.get("office", "")
        item.state = d.get("state", "")
        item.total_receipts = d.get("total_receipts", "")
        item.total_disbursements = d.get("total_disbursements", "")
        item.cash_on_hand = d.get("cash_on_hand", "")
        item.election_year = d.get("election_year", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Candidate {i}:")
        print(f"    Name:           {item.candidate_name}")
        print(f"    Party:          {item.party}")
        print(f"    Office:         {item.office}")
        print(f"    State:          {item.state}")
        print(f"    Receipts:       {item.total_receipts}")
        print(f"    Disbursements:  {item.total_disbursements}")
        print(f"    Cash on Hand:   {item.cash_on_hand}")
        print(f"    Election Year:  {item.election_year}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("fec")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = FecSearchRequest()
            result = fec_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} candidates")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
