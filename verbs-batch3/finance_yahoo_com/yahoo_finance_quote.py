"""
Playwright script (Python) — Yahoo Finance Stock Quote
Symbol: AAPL

Uses the user's Chrome profile for persistent login state.
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
class YahooFinanceQuoteRequest:
    symbol: str


@dataclass(frozen=True)
class YahooFinanceQuoteResult:
    name: str
    price: str
    change: str
    volume: str
    market_cap: str


# Navigates to Yahoo Finance for a given stock symbol, waits for the page to load,
# and extracts the current price, day change, volume, and market cap.
def yahoo_finance_quote(
    page: Page,
    request: YahooFinanceQuoteRequest,
) -> YahooFinanceQuoteResult:
    symbol = request.symbol

    print(f"  Symbol: {symbol}\n")

    url = f"https://finance.yahoo.com/quote/{symbol}/"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to Yahoo Finance quote page for {symbol}")
    page.goto(url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Find the stock name line containing the symbol in parentheses
    stock_name = symbol
    price = "N/A"
    change_amount = "N/A"
    change_pct = "N/A"
    volume = "N/A"
    market_cap = "N/A"

    for i, line in enumerate(lines):
        # Find stock name and price
        if f"({symbol})" in line and len(line) < 60:
            stock_name = line
            # Next line is the current price
            if i + 1 < len(lines):
                price_candidate = lines[i + 1]
                if re.match(r"^[\d,.]+$", price_candidate):
                    price = price_candidate
            # Day change amount (starts with + or -)
            if i + 2 < len(lines):
                chg = lines[i + 2]
                if re.match(r"^[+-]", chg):
                    change_amount = chg
            # Day change percentage
            if i + 3 < len(lines):
                pct = lines[i + 3]
                if pct.startswith("(") and "%" in pct:
                    change_pct = pct

        # Find volume
        if line == "Volume" and i + 1 < len(lines):
            volume = lines[i + 1]

        # Find market cap
        if "Market Cap" in line and i + 1 < len(lines):
            market_cap = lines[i + 1]

    result = YahooFinanceQuoteResult(
        name=stock_name,
        price=price,
        change=change_amount + " " + change_pct,
        volume=volume,
        market_cap=market_cap,
    )

    print("=" * 50)
    print(f"Stock Quote: {result.name}")
    print("=" * 50)
    print(f"  Current Price: ${result.price}")
    print(f"  Day Change:    {result.change}")
    print(f"  Volume:        {result.volume}")
    print(f"  Market Cap:    {result.market_cap}")

    return result


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    user_data = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default")

    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            user_data,
            executable_path=chrome_path,
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        result = yahoo_finance_quote(page, YahooFinanceQuoteRequest(symbol="AAPL"))
        print(f"\nResult: {result}")

        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)