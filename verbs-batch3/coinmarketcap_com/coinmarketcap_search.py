"""
Playwright script (Python) — CoinMarketCap Crypto Price Lookup
Query: Bitcoin

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
class CoinmarketcapRequest:
    query: str


@dataclass(frozen=True)
class CoinmarketcapResult:
    name: str
    price: str
    change_24h: str
    market_cap: str
    volume_24h: str


# Looks up a cryptocurrency on CoinMarketCap and returns its current price,
# 24h change, market cap, and 24h trading volume.
def lookup_coinmarketcap(
    page: Page,
    request: CoinmarketcapRequest,
) -> CoinmarketcapResult:
    query = request.query

    print(f"  Query: {query}\n")

    try:
        # ── Navigate ──────────────────────────────────────────────────
        print("Loading CoinMarketCap...")
        slug = query.lower().replace(" ", "-")
        url = f"https://coinmarketcap.com/currencies/{slug}/"
        checkpoint(f"Navigate to {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)
        print(f"  Loaded: {page.url}")

        # ── Extract crypto data ───────────────────────────────────────
        print("Extracting crypto data...")

        body_text = page.evaluate("document.body.innerText") or ""
        lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        price = "N/A"
        change_24h = "N/A"
        market_cap = "N/A"
        volume_24h = "N/A"

        for i, line in enumerate(lines):
            if price == "N/A" and re.match(r"^\$[\d,]+\.\d{2}$", line):
                price = line

            if "(24h)" in line and "%" in line:
                m = re.search(r"([\-\d.]+)%\s*\(24h\)", line)
                if m:
                    change_24h = m.group(1) + "%"

            if line == "Market cap" and i + 1 < len(lines):
                market_cap = lines[i + 1]

            if "Volume (24h)" in line:
                for j in range(i + 1, min(i + 4, len(lines))):
                    if lines[j].startswith("$"):
                        volume_24h = lines[j]
                        break

        result = CoinmarketcapResult(
            name=query,
            price=price,
            change_24h=change_24h,
            market_cap=market_cap,
            volume_24h=volume_24h,
        )

        # ── Print results ─────────────────────────────────────────────
        print(f"\n{result.name}:")
        print(f"  Current Price:    {result.price}")
        print(f"  24h Change:       {result.change_24h}")
        print(f"  Market Cap:       {result.market_cap}")
        print(f"  24h Volume:       {result.volume_24h}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
        result = CoinmarketcapResult(
            name=query,
            price="N/A",
            change_24h="N/A",
            market_cap="N/A",
            volume_24h="N/A",
        )

    return result


def test_lookup_coinmarketcap() -> None:
    request = CoinmarketcapRequest(
        query="Bitcoin",
    )

    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=False,
            viewport=None,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = lookup_coinmarketcap(page, request)
            assert result.name == request.query
            print(f"\nLookup complete for: {result.name}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_lookup_coinmarketcap)
