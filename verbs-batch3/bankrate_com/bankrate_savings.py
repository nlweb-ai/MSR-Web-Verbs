"""
Playwright script (Python) — Bankrate.com Best Savings Rates
Max results: 5

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
class BankrateSavingsRequest:
    max_results: int


@dataclass(frozen=True)
class BankrateSavingsOffer:
    bank_name: str
    apy: str
    min_deposit: str


@dataclass(frozen=True)
class BankrateSavingsResult:
    offers: list[BankrateSavingsOffer]


# Scrapes Bankrate's best high-yield savings accounts page and returns up to max_results
# offers with bank name, APY, and minimum deposit.
def get_bankrate_savings(
    page: Page,
    request: BankrateSavingsRequest,
) -> BankrateSavingsResult:
    max_results = request.max_results

    print(f"  Max results: {max_results}\n")

    results: list[BankrateSavingsOffer] = []

    try:
        # ── Navigate ──────────────────────────────────────────────────────
        print("Loading Bankrate best savings rates page...")
        checkpoint("Navigate to Bankrate savings page")
        page.goto("https://www.bankrate.com/banking/savings/best-high-yield-interests-savings-accounts/")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)
        print(f"  Loaded: {page.url}")

        # ── Extract savings accounts ──────────────────────────────────────
        print(f"Extracting up to {max_results} savings accounts...")

        body_text = page.evaluate("document.body.innerText") or ""
        lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        seen_banks = set()
        i = 0
        while i < len(lines) and len(results) < max_results:
            line = lines[i]

            if "APY as of" in line:
                apy = "N/A"
                for k in range(i + 1, min(i + 4, len(lines))):
                    m = re.match(r"^(\d+\.\d+)$", lines[k])
                    if m:
                        apy = m.group(1) + "%"
                        break

                min_deposit = "N/A"
                for k in range(i + 1, min(i + 10, len(lines))):
                    if "Min. balance for APY" in lines[k]:
                        for j2 in range(k + 1, min(k + 4, len(lines))):
                            if lines[j2] == "$":
                                if j2 + 1 < len(lines):
                                    min_deposit = "$" + lines[j2 + 1].replace(",", "")
                                break
                        break

                bank_name = "N/A"
                for k in range(i - 1, max(0, i - 12), -1):
                    if lines[k] == "Add to compare" and k > 0:
                        bank_name = lines[k - 1]
                        break
                    if lines[k] in ("EDITOR'S PICK",) and k + 1 < len(lines):
                        bank_name = lines[k + 1]
                        break

                if bank_name != "N/A" and apy != "N/A" and bank_name not in seen_banks:
                    seen_banks.add(bank_name)
                    results.append(BankrateSavingsOffer(
                        bank_name=bank_name,
                        apy=apy,
                        min_deposit=min_deposit,
                    ))

            i += 1

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nFound {len(results)} savings account offers:\n")
        for i, offer in enumerate(results, 1):
            print(f"  {i}. {offer.bank_name}")
            print(f"     APY: {offer.apy}  Min deposit: {offer.min_deposit}")
            print()

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return BankrateSavingsResult(
        offers=results,
    )


def test_get_bankrate_savings() -> None:
    request = BankrateSavingsRequest(
        max_results=5,
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
            result = get_bankrate_savings(page, request)
            assert len(result.offers) <= request.max_results
            print(f"\nTotal offers found: {len(result.offers)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_get_bankrate_savings)
