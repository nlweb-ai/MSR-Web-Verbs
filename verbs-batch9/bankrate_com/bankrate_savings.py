"""
Playwright script (Python) — Bankrate Savings Rates
Look up high-yield savings account rates on Bankrate.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BankrateSavingsRequest:
    max_results: int = 5


@dataclass
class SavingsAccountItem:
    bank_name: str = ""
    apy: str = ""
    min_deposit: str = ""
    monthly_fee: str = ""


@dataclass
class BankrateSavingsResult:
    items: List[SavingsAccountItem] = field(default_factory=list)


def get_bankrate_savings(page: Page, request: BankrateSavingsRequest) -> BankrateSavingsResult:
    """Look up high-yield savings account rates on Bankrate."""
    url = "https://www.bankrate.com/banking/savings/best-high-yield-interests-savings-accounts/"
    print(f"Loading {url}...")
    checkpoint("Navigate to savings rates")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    result = BankrateSavingsResult()

    checkpoint("Extract savings accounts")
    js_code = """(max) => {
        const items = [];
        const cards = document.querySelectorAll('[class*="product-card"], [class*="ProductCard"], [class*="rate-card"], tr, [class*="listing"], article');
        for (const card of cards) {
            if (items.length >= max) break;
            const text = (card.textContent || '').replace(/\\s+/g, ' ').trim();

            let name = '';
            const nameEl = card.querySelector('h2, h3, h4, [class*="name"], [class*="title"], [class*="bank"]');
            if (nameEl) name = nameEl.textContent.trim();
            if (!name || name.length < 3 || name.length > 80) continue;
            if (items.some(i => i.bank_name === name)) continue;

            let apy = '';
            const apyMatch = text.match(/(\\d+\\.\\d+)\\s*%\\s*APY/i);
            if (apyMatch) apy = apyMatch[1] + '% APY';
            if (!apy) {
                const apyMatch2 = text.match(/(\\d+\\.\\d+)%/);
                if (apyMatch2) apy = apyMatch2[1] + '%';
            }

            let minDeposit = '';
            const minMatch = text.match(/(?:min(?:imum)?\\s*(?:deposit|balance)?[:\\s]*)?\\$([\\d,]+)/i);
            if (minMatch) minDeposit = '$' + minMatch[1];

            let fee = '';
            const feeMatch = text.match(/(no\\s*(?:monthly\\s*)?fee|\\$[\\d.]+\\s*(?:monthly|per month|fee))/i);
            if (feeMatch) fee = feeMatch[1];

            items.push({bank_name: name, apy: apy, min_deposit: minDeposit, monthly_fee: fee});
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = SavingsAccountItem()
        item.bank_name = d.get("bank_name", "")
        item.apy = d.get("apy", "")
        item.min_deposit = d.get("min_deposit", "")
        item.monthly_fee = d.get("monthly_fee", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} savings accounts:")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.bank_name}")
        print(f"     APY: {item.apy}  Min Deposit: {item.min_deposit}  Fee: {item.monthly_fee}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("bankrate")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = get_bankrate_savings(page, BankrateSavingsRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} accounts")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
