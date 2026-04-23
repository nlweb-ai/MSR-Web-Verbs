import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class MorningstarFundRequest:
    ticker: str = "VFIAX"

@dataclass(frozen=True)
class MorningstarFundResult:
    fund_name: str = ""
    ticker: str = ""
    nav_price: str = ""
    morningstar_rating: str = ""
    expense_ratio: str = ""
    ytd_return: str = ""

# Look up a mutual fund on Morningstar by ticker symbol and extract
# fund name, NAV price, Morningstar rating, expense ratio, and YTD return.
def morningstar_fund(page: Page, request: MorningstarFundRequest) -> MorningstarFundResult:
    ticker = request.ticker.upper()
    print(f"  Ticker: {ticker}\n")

    url = f"https://www.morningstar.com/funds/xnas/{ticker.lower()}/quote"
    print(f"Loading {url}...")
    checkpoint("Navigate to Morningstar")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""

    fund_name = "N/A"
    nav_price = "N/A"
    morningstar_rating = "N/A"
    expense_ratio = "N/A"
    ytd_return = "N/A"

    # Extract fund name — typically the first prominent heading
    name_el = page.locator('h1, [class*="fundName"], [class*="security-name"], [data-testid*="name"]')
    if name_el.count() > 0:
        try:
            fund_name = name_el.first.inner_text(timeout=3000).strip()
        except Exception:
            pass

    # Fallback: try to find fund name from body text
    if fund_name == "N/A":
        # Look for a line containing the ticker
        for line in body_text.split("\n"):
            line = line.strip()
            if ticker in line.upper() and len(line) > len(ticker) + 5:
                fund_name = line
                break

    # Extract NAV price from the quote value section
    nav_el = page.locator('.quote__value__mdc .mdc-data-point--number')
    if nav_el.count() > 0:
        try:
            txt = nav_el.first.inner_text(timeout=3000).strip()
            m = re.search(r'[\d,]+\.\d{2}', txt)
            if m:
                nav_price = "$" + m.group(0)
        except Exception:
            pass

    # Fallback: parse body text lines after "NAV / 1-Day Return"
    if nav_price == "N/A":
        lines = body_text.split("\n")
        for i, line in enumerate(lines):
            if "NAV" in line and "Return" in line:
                for j in range(i + 1, min(i + 5, len(lines))):
                    m = re.search(r'([\d,]+\.\d{2})', lines[j])
                    if m:
                        nav_price = "$" + m.group(1)
                        break
                break

    # Extract Morningstar star rating from aria-label
    star_el = page.locator('span.mdc-star-rating[aria-label]')
    if star_el.count() > 0:
        try:
            aria = star_el.first.get_attribute('aria-label') or ''
            rm = re.search(r'(\d)\s*out\s*of\s*(\d)', aria, re.IGNORECASE)
            if rm:
                morningstar_rating = f"{rm.group(1)}/{rm.group(2)} stars"
        except Exception:
            pass

    # Fallback: look for "rating of X out of Y" in body text
    if morningstar_rating == "N/A":
        rm = re.search(r'rating\s+of\s+(\d)\s+out\s+of\s+(\d)', body_text, re.IGNORECASE)
        if rm:
            morningstar_rating = f"{rm.group(1)}/{rm.group(2)} stars"

    # Extract expense ratio
    er_match = re.search(r'(?:Expense\s*Ratio|Prospectus\s*Net\s*Expense)[^\d]{0,20}([\d.]+%)', body_text, re.IGNORECASE)
    if er_match:
        expense_ratio = er_match.group(1)

    # Extract YTD return from body text — find "YTD" line, then first number after it
    ytd_match = re.search(r'(?:YTD|Year.to.Date)[^\d-]{0,20}(-?[\d.]+%)', body_text, re.IGNORECASE)
    if ytd_match:
        ytd_return = ytd_match.group(1)
    else:
        lines = body_text.split("\n")
        for i, line in enumerate(lines):
            if line.strip() == "YTD":
                for j in range(i + 1, min(i + 10, len(lines))):
                    m = re.search(r'^(-?[\d.]+)$', lines[j].strip())
                    if m:
                        ytd_return = m.group(1) + "%"
                        break
                break

    print("=" * 60)
    print(f"Morningstar - Fund Details for {ticker}")
    print("=" * 60)
    print(f"  Fund Name:          {fund_name}")
    print(f"  Ticker:             {ticker}")
    print(f"  NAV Price:          {nav_price}")
    print(f"  Morningstar Rating: {morningstar_rating}")
    print(f"  Expense Ratio:      {expense_ratio}")
    print(f"  YTD Return:         {ytd_return}")

    return MorningstarFundResult(
        fund_name=fund_name,
        ticker=ticker,
        nav_price=nav_price,
        morningstar_rating=morningstar_rating,
        expense_ratio=expense_ratio,
        ytd_return=ytd_return,
    )

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = morningstar_fund(page, MorningstarFundRequest())
        print(f"\nFund: {result.fund_name} ({result.ticker})")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
