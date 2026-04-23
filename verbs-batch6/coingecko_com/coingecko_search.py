"""
Auto-generated Playwright script (Python)
CoinGecko – Cryptocurrency Info
Coin: "ethereum"

Generated on: 2026-04-18T05:07:23.993Z
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
class CoinRequest:
    coin: str = "ethereum"


@dataclass
class CoinResult:
    name: str = ""
    price: str = ""
    change_24h: str = ""
    volume_24h: str = ""
    market_cap: str = ""
    all_time_high: str = ""


def coingecko_search(page: Page, request: CoinRequest) -> CoinResult:
    """Get cryptocurrency info from CoinGecko."""
    print(f"  Coin: {request.coin}\n")

    url = f"https://www.coingecko.com/en/coins/{request.coin}"
    print(f"Loading {url}...")
    checkpoint("Navigate to CoinGecko coin page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract coin data")
    body_text = page.evaluate("document.body.innerText") or ""

    name = request.coin.title()
    price = ""
    change_24h = ""
    volume_24h = ""
    market_cap = ""
    all_time_high = ""

    try:
        h1 = page.locator("h1").first
        if h1.is_visible(timeout=2000):
            name = h1.inner_text().strip()
    except Exception:
        pass

    pm = re.search(r"\$(\d[\d,.]*)", body_text)
    if pm:
        price = "$" + pm.group(1)

    chm = re.search(r"([+-]?\d+\.?\d*)%", body_text)
    if chm:
        change_24h = chm.group(0)

    volm = re.search(r"(?:24[hH]?\s*(?:Trading\s*)?Volume)[:\s]*\$(\d[\d,.]*[BKMGT]?)", body_text, re.IGNORECASE)
    if volm:
        volume_24h = "$" + volm.group(1)

    mcm = re.search(r"(?:Market\s*Cap)[:\s]*\$(\d[\d,.]*[BKMGT]?)", body_text, re.IGNORECASE)
    if mcm:
        market_cap = "$" + mcm.group(1)

    athm = re.search(r"(?:All.?Time\s*High)[:\s]*\$(\d[\d,.]*)", body_text, re.IGNORECASE)
    if athm:
        all_time_high = "$" + athm.group(1)

    result = CoinResult(
        name=name, price=price, change_24h=change_24h,
        volume_24h=volume_24h, market_cap=market_cap,
        all_time_high=all_time_high,
    )

    print("\n" + "=" * 60)
    print(f"CoinGecko: {result.name}")
    print("=" * 60)
    print(f"  Price:          {result.price}")
    print(f"  24h Change:     {result.change_24h}")
    print(f"  24h Volume:     {result.volume_24h}")
    print(f"  Market Cap:     {result.market_cap}")
    print(f"  All-Time High:  {result.all_time_high}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("coingecko_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = coingecko_search(page, CoinRequest())
            print(f"\nReturned info for {result.name}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
