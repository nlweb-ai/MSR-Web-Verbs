"""
Auto-generated Playwright script (Python)
Congress.gov – Legislation Search
Search for legislation and extract bill details.

Generated on: 2026-04-16T21:57:46.509Z
Recorded 1 browser interactions
"""

import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class CongressLegislationRequest:
    query: str = "infrastructure bill"
    max_results: int = 5

@dataclass(frozen=True)
class CongressBill:
    bill_number: str = ""
    title: str = ""
    sponsor: str = ""
    date_introduced: str = ""
    status: str = ""

@dataclass(frozen=True)
class CongressLegislationResult:
    bills: list = None  # list[CongressBill]

def congress_legislation(page: Page, request: CongressLegislationRequest) -> CongressLegislationResult:
    query = request.query
    max_results = request.max_results
    print(f"  Search query: {query}")
    print(f"  Max results to extract: {max_results}\n")

    url = f"https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22search%22%3A%22{query.replace(' ', '+')}%22%7D"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to Congress.gov legislation search for '{query}'")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    print(f"  Loaded: {page.url}")

    results = []

    items = page.locator('ol.basic-search-results-lists li.expanded')
    count = items.count()
    print(f"  Found {count} search result items via selector")

    for i in range(min(count, max_results)):
        item = items.nth(i)
        try:
            bill_number = "N/A"
            title = "N/A"
            sponsor = "N/A"
            date_introduced = "N/A"
            status = "N/A"

            # Bill number from heading link
            heading = item.locator('span.result-heading a')
            if heading.count() > 0:
                bill_number = heading.first.inner_text(timeout=3000).strip()
                # Title is the link text after bill number on the full heading
                heading_full = item.locator('span.result-heading')
                full_text = heading_full.first.inner_text(timeout=3000).strip()
                rest = full_text.replace(bill_number, "", 1).strip()
                if rest.startswith("\u2014") or rest.startswith("-"):
                    rest = rest.lstrip("\u2014- ").strip()
                if rest and len(rest) > 5:
                    title = rest

            # Parse result-item spans for sponsor, date, latest action, tracker
            detail_spans = item.locator('span.result-item')
            for j in range(detail_spans.count()):
                txt = detail_spans.nth(j).inner_text(timeout=3000).strip()
                sm = re.match(r'Sponsor:\s*(.+?)(?:\s*\(Introduced\s+(\d{1,2}/\d{1,2}/\d{4})\))?(?:\s*Cosponsors.*)?$', txt, re.I)
                if sm:
                    sponsor = sm.group(1).strip()
                    if sm.group(2):
                        date_introduced = sm.group(2).strip()
                    continue
                lm = re.match(r'Latest Action:\s*(.+?)(?:\s*\(All Actions\))?\s*$', txt, re.I | re.S)
                if lm:
                    status = lm.group(1).strip()
                    continue
                tm = re.search(r'has the status\s+(\w[\w\s]*\w)', txt, re.I)
                if tm and status == "N/A":
                    status = tm.group(1).strip()

            if bill_number != "N/A" or title != "N/A":
                results.append(CongressBill(
                    bill_number=bill_number,
                    title=title,
                    sponsor=sponsor,
                    date_introduced=date_introduced,
                    status=status,
                ))
        except Exception:
            continue

    print("=" * 60)
    print(f"Congress.gov - Legislation Search: '{query}'")
    print("=" * 60)
    for idx, b in enumerate(results, 1):
        print(f"\n{idx}. {b.bill_number}")
        print(f"   Title: {b.title}")
        print(f"   Sponsor: {b.sponsor}")
        print(f"   Introduced: {b.date_introduced}")
        print(f"   Status: {b.status}")

    print(f"\nFound {len(results)} bills")

    return CongressLegislationResult(bills=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = congress_legislation(page, CongressLegislationRequest())
        print(f"\nReturned {len(result.bills or [])} bills")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
