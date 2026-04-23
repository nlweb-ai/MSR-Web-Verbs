"""
Playwright script (Python) — MarketBeat Stock Info
Look up stock information on MarketBeat.
"""

import os, sys, shutil
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MarketBeatRequest:
    ticker: str = "AAPL"


@dataclass
class StockInfo:
    ticker: str = ""
    price: str = ""
    market_cap: str = ""
    pe_ratio: str = ""
    dividend_yield: str = ""
    high_52w: str = ""
    low_52w: str = ""
    analyst_rating: str = ""


# Looks up stock information on MarketBeat for the given ticker
# and returns price, market cap, P/E, dividend yield, 52-week range, analyst rating.
def lookup_marketbeat_stock(page: Page, request: MarketBeatRequest) -> StockInfo:
    url = f"https://www.marketbeat.com/stocks/NASDAQ/{request.ticker}/"
    print(f"Loading {url}...")
    checkpoint("Navigate to MarketBeat stock page")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)

    result = StockInfo(ticker=request.ticker)

    checkpoint("Extract stock data")
    js_code = """() => {
        const data = {};
        const text = document.body.innerText;

        // Price - look for dollar amount near the ticker
        const priceMatch = text.match(/\\$([\\d,.]+)\\s/);
        if (priceMatch) data.price = '$' + priceMatch[1];

        // Market Cap
        const mcMatch = text.match(/Market\\s*Cap[:\\s]*([\\$\\d,.]+\\s*[BMT](?:illion)?)/i);
        if (mcMatch) data.market_cap = mcMatch[1];

        // P/E Ratio
        const peMatch = text.match(/P\\/E\\s*Ratio[:\\s]*([-\\d,.]+)/i);
        if (peMatch) data.pe_ratio = peMatch[1];

        // Dividend Yield
        const divMatch = text.match(/Dividend\\s*Yield[:\\s]*([-\\d,.]+%?)/i);
        if (divMatch) data.dividend_yield = divMatch[1];

        // 52-Week Range - values are on separate lines after the label
        const lines = text.split('\\n').map(l => l.trim());
        const rangeIdx = lines.findIndex(l => /52.Week Range/i.test(l));
        if (rangeIdx >= 0) {
            const prices = [];
            for (let ri = rangeIdx + 1; ri < Math.min(rangeIdx + 5, lines.length); ri++) {
                const pm = lines[ri].match(/^\\$([\\d,.]+)/);
                if (pm) prices.push(pm[1]);
            }
            if (prices.length >= 2) { data.low_52w = '$' + prices[0]; data.high_52w = '$' + prices[1]; }
        }

        // Analyst Rating
        const analystMatch = text.match(/(?:Consensus|Analyst)\\s*Rating[:\\s]*([\\w\\s]+?)(?:\\n|$)/i);
        if (analystMatch) data.analyst_rating = analystMatch[1].trim();

        return data;
    }"""
    data = page.evaluate(js_code)

    result.price = data.get("price", "")
    result.market_cap = data.get("market_cap", "")
    result.pe_ratio = data.get("pe_ratio", "")
    result.dividend_yield = data.get("dividend_yield", "")
    result.high_52w = data.get("high_52w", "")
    result.low_52w = data.get("low_52w", "")
    result.analyst_rating = data.get("analyst_rating", "")

    print(f"\nStock info for {request.ticker}:")
    print(f"  Price: {result.price}")
    print(f"  Market Cap: {result.market_cap}")
    print(f"  P/E Ratio: {result.pe_ratio}")
    print(f"  Dividend Yield: {result.dividend_yield}")
    print(f"  52-Week High: {result.high_52w}")
    print(f"  52-Week Low: {result.low_52w}")
    print(f"  Analyst Rating: {result.analyst_rating}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("marketbeat")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = lookup_marketbeat_stock(page, MarketBeatRequest())
            print("\n=== DONE ===")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
