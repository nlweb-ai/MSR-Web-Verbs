import re
import os
from dataclasses import dataclass
from urllib.parse import quote as url_quote
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class EdgarSearchRequest:
    ticker: str = "TSLA"
    max_results: int = 5

@dataclass(frozen=True)
class EdgarFiling:
    filing_type: str = ""
    filing_date: str = ""
    description: str = ""
    filing_link: str = ""

@dataclass(frozen=True)
class EdgarSearchResult:
    filings: list = None  # list[EdgarFiling]

# Search SEC EDGAR for company filings by ticker symbol
# and extract filing type, date, description, and link.
def edgar_search(page: Page, request: EdgarSearchRequest) -> EdgarSearchResult:
    ticker = request.ticker
    max_results = request.max_results
    print(f"  Ticker: {ticker}")
    print(f"  Max results: {max_results}\n")

    company_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=&CIK={url_quote(ticker)}&type=&dateb=&owner=include&count=40&search_text=&action=getcompany"
    print(f"Loading EDGAR company filings for {ticker}...")
    checkpoint("Navigate to EDGAR company filings page")
    page.goto(company_url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    print(f"  Loaded: {page.url}")

    # Check if redirected to new EDGAR interface
    if "efts" in page.url or "edgar/browse" in page.url:
        print("  Using new EDGAR interface...")
        new_url = f"https://efts.sec.gov/LATEST/search-index?q=%22{url_quote(ticker)}%22&forms=10-K,10-Q,8-K"
        checkpoint("Navigate to EDGAR full-text search")
        page.goto(new_url, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

    results = []

    # Extract filings from the old EDGAR table
    checkpoint("Extract filings from search results")
    filing_rows = page.locator('table.tableFile2 tr')
    count = filing_rows.count()
    print(f"  Found {count} table rows")

    if count > 1:  # Skip header row
        for i in range(1, min(count, max_results + 1)):
            row = filing_rows.nth(i)
            try:
                cells = row.locator('td')
                if cells.count() < 4:
                    continue

                filing_type = cells.nth(0).inner_text(timeout=2000).strip()
                filing_link = "N/A"
                try:
                    link = cells.nth(1).locator('a').first
                    filing_link = link.get_attribute("href", timeout=2000) or "N/A"
                    if filing_link.startswith("/"):
                        filing_link = f"https://www.sec.gov{filing_link}"
                except Exception:
                    pass
                description = cells.nth(2).inner_text(timeout=2000).strip()
                filing_date = cells.nth(3).inner_text(timeout=2000).strip()

                results.append(EdgarFiling(
                    filing_type=filing_type,
                    filing_date=filing_date,
                    description=description,
                    filing_link=filing_link,
                ))
            except Exception:
                continue
    else:
        # Fallback: extract from body text using regex
        print("  Trying body text fallback...")
        body_text = page.evaluate("document.body.innerText") or ""
        pattern = re.compile(
            r'(10-K|10-Q|8-K|S-1|DEF 14A|13F)\s+'
            r'(\d{4}-\d{2}-\d{2})\s+'
            r'(.+?)(?:\n|$)',
            re.MULTILINE
        )
        for m in pattern.finditer(body_text):
            if len(results) >= max_results:
                break
            results.append(EdgarFiling(
                filing_type=m.group(1),
                filing_date=m.group(2),
                description=m.group(3).strip()[:100],
                filing_link="N/A",
            ))

    print("=" * 60)
    print(f"SEC EDGAR - Filings for \"{ticker}\"")
    print("=" * 60)
    for idx, f in enumerate(results, 1):
        print(f"\n{idx}. {f.filing_type} - {f.filing_date}")
        print(f"   Description: {f.description[:80]}")
        print(f"   Link: {f.filing_link[:80]}")

    print(f"\nFound {len(results)} filings")

    return EdgarSearchResult(filings=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = edgar_search(page, EdgarSearchRequest())
        print(f"\nReturned {len(result.filings or [])} filings")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
