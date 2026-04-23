"""
Playwright script (Python) — KBB Vehicle Value Lookup
Look up Kelley Blue Book value for a vehicle by make, model, and year.
Extract trade-in value, private party value, suggested retail price, and fair market range.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class KBBRequest:
    make: str = "toyota"
    model: str = "rav4"
    year: str = "2021"


@dataclass
class KBBResult:
    make: str = ""
    model: str = ""
    year: str = ""
    trade_in: str = ""
    private_party: str = ""
    fair_purchase_price: str = ""
    displayed_prices: List[str] = field(default_factory=list)


# Looks up the Kelley Blue Book value for a vehicle specified by make, model, and year.
# Returns trade-in value, private party value, suggested retail price, and fair market range.
def lookup_kbb_value(page: Page, request: KBBRequest) -> KBBResult:
    url = f"https://www.kbb.com/{request.make}/{request.model}/{request.year}/"
    print(f"Loading {url}...")
    checkpoint("Navigate to KBB vehicle page")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = KBBResult(make=request.make, model=request.model, year=request.year)

    checkpoint("Extract vehicle values")
    js_code = """() => {
        const text = document.body.innerText;
        const result = { trade_in: '', private_party: '', fair_purchase_price: '', displayed_prices: [] };
        const lines = text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);

        // Find the pricing table section: "Trade-In Value" / "Private Party Value" / "Fair Purchase Price"
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === 'Trade-In Value' && i + 1 < lines.length && lines[i+1] === 'Private Party Value') {
                // Next lines with $ are the first trim's values
                let priceLines = [];
                for (let j = i + 3; j < Math.min(i + 10, lines.length); j++) {
                    if (lines[j].match(/^\\$/)) priceLines.push(lines[j]);
                    if (priceLines.length >= 3) break;
                }
                if (priceLines.length >= 3) {
                    result.trade_in = priceLines[0];
                    result.private_party = priceLines[1];
                    result.fair_purchase_price = priceLines[2];
                }
                break;
            }
        }

        // Fallback: regex on full text
        if (!result.trade_in) {
            const tradeMatch = text.match(/trade.?in.*?(\\$[\\d,]+)/i);
            if (tradeMatch) result.trade_in = tradeMatch[1];
        }
        if (!result.private_party) {
            const privateMatch = text.match(/private\\s*party.*?(\\$[\\d,]+)/i);
            if (privateMatch) result.private_party = privateMatch[1];
        }
        if (!result.fair_purchase_price) {
            const fairMatch = text.match(/fair\\s*purchase\\s*price.*?(\\$[\\d,]+)/i);
            if (fairMatch) result.fair_purchase_price = fairMatch[1];
        }

        return result;
    }"""
    data = page.evaluate(js_code)

    result.trade_in = data.get("trade_in", "")
    result.private_party = data.get("private_party", "")
    result.fair_purchase_price = data.get("fair_purchase_price", "")

    print(f"\nKBB Values for {request.year} {request.make.title()} {request.model.upper()}:")
    print(f"  Trade-in: {result.trade_in}")
    print(f"  Private Party: {result.private_party}")
    print(f"  Fair Purchase Price: {result.fair_purchase_price}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("kbb")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = lookup_kbb_value(page, KBBRequest())
            print("\n=== DONE ===")
            print(f"Trade-in: {result.trade_in}")
            print(f"Private Party: {result.private_party}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
