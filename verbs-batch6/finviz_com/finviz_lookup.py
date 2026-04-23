"""
Auto-generated Playwright script (Python)
Finviz – Stock Lookup
Ticker: "MSFT"

Generated on: 2026-04-18T05:21:30.348Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class StockRequest:
    ticker: str = "MSFT"


@dataclass
class StockResult:
    ticker: str = ""
    price: str = ""
    market_cap: str = ""
    pe_ratio: str = ""
    eps: str = ""
    dividend_yield: str = ""
    week52_range: str = ""
    target_price: str = ""


def finviz_lookup(page: Page, request: StockRequest) -> StockResult:
    """Look up stock info on Finviz."""
    print(f"  Ticker: {request.ticker}\n")

    url = f"https://finviz.com/quote.ashx?t={request.ticker}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Finviz quote page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract stock metrics")
    metrics = page.evaluate(r"""() => {
        const data = {};
        const rows = document.querySelectorAll('table.snapshot-table2 tr, table[class*="snapshot"] tr');
        for (const row of rows) {
            const cells = row.querySelectorAll('td');
            for (let i = 0; i < cells.length - 1; i += 2) {
                const key = (cells[i]?.innerText || '').trim();
                const val = (cells[i+1]?.innerText || '').trim();
                if (key) data[key] = val;
            }
        }
        return data;
    }""")

    price = metrics.get("Price", "") if hasattr(metrics, 'get') else ""
    market_cap = metrics.get("Market Cap", "")
    pe = metrics.get("P/E", "")
    eps = metrics.get("EPS (ttm)", "") or metrics.get("EPS", "")
    div_yield = metrics.get("Dividend %", "") or metrics.get("Dividend", "")
    w52 = metrics.get("52W Range", "")
    target = metrics.get("Target Price", "")

    # fallback: try dict-like access
    if not price and isinstance(metrics, dict):
        for k, v in metrics.items():
            kl = k.lower()
            if kl == "price": price = v
            elif "market cap" in kl: market_cap = v
            elif kl == "p/e": pe = v
            elif "eps" in kl and not eps: eps = v
            elif "dividend" in kl and not div_yield: div_yield = v
            elif "52w" in kl and not w52: w52 = v
            elif "target" in kl and not target: target = v

    result = StockResult(
        ticker=request.ticker, price=price, market_cap=market_cap,
        pe_ratio=pe, eps=eps, dividend_yield=div_yield,
        week52_range=w52, target_price=target,
    )

    print("\n" + "=" * 60)
    print(f"Finviz: {result.ticker}")
    print("=" * 60)
    print(f"  Price:          {result.price}")
    print(f"  Market Cap:     {result.market_cap}")
    print(f"  P/E Ratio:      {result.pe_ratio}")
    print(f"  EPS:            {result.eps}")
    print(f"  Dividend Yield: {result.dividend_yield}")
    print(f"  52-Week Range:  {result.week52_range}")
    print(f"  Target Price:   {result.target_price}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("finviz_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = finviz_lookup(page, StockRequest())
            print(f"\nReturned info for {result.ticker}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
