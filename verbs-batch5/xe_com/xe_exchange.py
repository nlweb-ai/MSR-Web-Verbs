"""
Auto-generated Playwright script (Python)
XE – Currency Exchange Rate Lookup
From: USD, To: EUR

Generated on: 2026-04-18T03:08:55.529Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class XERequest:
    from_currency: str = "USD"
    to_currency: str = "EUR"


@dataclass
class ExchangeRate:
    from_currency: str = ""
    to_currency: str = ""
    current_rate: str = ""
    inverse_rate: str = ""
    high_30d: str = ""
    low_30d: str = ""
    avg_30d: str = ""
    volatility_30d: str = ""


def xe_lookup(page: Page, request: XERequest) -> ExchangeRate:
    """Look up currency exchange rate on XE."""
    print(f"  From: {request.from_currency}")
    print(f"  To:   {request.to_currency}\n")

    # ── Navigate to converter ─────────────────────────────────────────
    url = f"https://www.xe.com/currencyconverter/convert/?Amount=1&From={request.from_currency}&To={request.to_currency}"
    print(f"Loading {url}...")
    checkpoint("Navigate to XE converter")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    # Scroll to load statistics section
    for _ in range(3):
        page.evaluate("window.scrollBy(0, 1500)")
        page.wait_for_timeout(500)

    # ── Extract rates ─────────────────────────────────────────────────
    data = page.evaluate(r"""(args) => {
        const { from_cur, to_cur } = args;
        const text = document.body.innerText;

        // Current rate: "1.00 USD = 0.85005031 EUR"
        let currentRate = '';
        const rateMatch = text.match(new RegExp('1\\.00\\s+' + from_cur + '\\s*=\\s*([\\d.]+)\\s+' + to_cur));
        if (rateMatch) currentRate = rateMatch[1];

        // Inverse rate: from the conversion table "1 EUR   1.1764 USD"
        let inverseRate = '';
        const invMatch = text.match(new RegExp('1\\s+' + to_cur + '\\s+([\\d.]+)\\s+' + from_cur));
        if (invMatch) inverseRate = invMatch[1];

        // 30-day stats from the statistics table
        // Pattern: High (next line) 0.8565 0.8729 0.8745 (7d, 30d, 90d)
        const NL = String.fromCharCode(10);
        const lines = text.split(NL);
        let high30 = '', low30 = '', avg30 = '', vol30 = '';

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (line === 'High' && i + 1 < lines.length) {
                const vals = lines[i + 1].trim().split(/\s+/);
                if (vals.length >= 2) high30 = vals[1]; // 30-day is second
            }
            if (line === 'Low' && i + 1 < lines.length) {
                const vals = lines[i + 1].trim().split(/\s+/);
                if (vals.length >= 2) low30 = vals[1];
            }
            if (line === 'Average' && i + 1 < lines.length) {
                const vals = lines[i + 1].trim().split(/\s+/);
                if (vals.length >= 2) avg30 = vals[1];
            }
            if (line === 'Volatility' && i + 1 < lines.length) {
                const vals = lines[i + 1].trim().split(/\s+/);
                if (vals.length >= 2) vol30 = vals[1];
            }
        }

        return { currentRate, inverseRate, high30, low30, avg30, vol30 };
    }""", {"from_cur": request.from_currency, "to_cur": request.to_currency})

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"XE: {request.from_currency} → {request.to_currency}")
    print("=" * 60)
    print(f"\n  Current Rate:  1 {request.from_currency} = {data['currentRate']} {request.to_currency}")
    print(f"  Inverse Rate:  1 {request.to_currency} = {data['inverseRate']} {request.from_currency}")
    print(f"\n  30-Day Statistics:")
    print(f"    High:        {data['high30']}")
    print(f"    Low:         {data['low30']}")
    print(f"    Average:     {data['avg30']}")
    print(f"    Volatility:  {data['vol30']}")

    return ExchangeRate(
        from_currency=request.from_currency,
        to_currency=request.to_currency,
        current_rate=data['currentRate'],
        inverse_rate=data['inverseRate'],
        high_30d=data['high30'],
        low_30d=data['low30'],
        avg_30d=data['avg30'],
        volatility_30d=data['vol30'],
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("xe_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = xe_lookup(page, XERequest())
            print(f"\nReturned: 1 {result.from_currency} = {result.current_rate} {result.to_currency}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
