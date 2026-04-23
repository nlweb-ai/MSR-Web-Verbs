"""
Playwright script (Python) — Target Weekly Deals
List Target deals with name, original price, and sale price.

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
class TargetDealsRequest:
    section: str
    max_results: int


@dataclass(frozen=True)
class TargetDeal:
    name: str
    original_price: str
    sale_price: str


@dataclass(frozen=True)
class TargetDealsResult:
    section: str
    deals: list[TargetDeal]


# Lists Target weekly deals from the Circle deals page, extracting
# up to max_results deals with name, original price, and sale price.
def list_target_deals(
    page: Page,
    request: TargetDealsRequest,
) -> TargetDealsResult:
    section = request.section
    max_results = request.max_results

    print(f"  Section: {section}\n")

    results: list[TargetDeal] = []

    try:
        checkpoint("Navigate to https://www.target.com/circle/deals")
        page.goto("https://www.target.com/circle/deals")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)

        for sel in ["button#onetrust-accept-btn-handler", "button:has-text('Accept')", "button:has-text('Close')"]:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {sel}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        links = page.locator("a[href*='/p/']")
        count = links.count()
        seen = set()

        for i in range(count):
            if len(results) >= max_results:
                break
            link = links.nth(i)
            href = link.get_attribute("href", timeout=2000) or ""
            if href in seen:
                continue
            seen.add(href)
            parent_txt = link.locator("..").inner_text(timeout=2000).strip()
            if not parent_txt:
                continue
            lines = [l.strip() for l in parent_txt.split("\n") if l.strip()]
            name = lines[-1] if lines else "N/A"
            price = "N/A"
            deal = "N/A"
            for line in lines:
                if "$" in line and price == "N/A":
                    price = line
                if any(kw in line.lower() for kw in ["off", "save", "buy", "sale"]) and deal == "N/A":
                    deal = line
            results.append(TargetDeal(name=name[:100], original_price=price, sale_price=deal))
            print(f"  {len(results)}. {name[:80]} | {price} | {deal}")

        print(f"\nFound {len(results)} deals:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name} — was {r.original_price}, now {r.sale_price}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return TargetDealsResult(section=section, deals=results)


def test_list_target_deals() -> None:
    request = TargetDealsRequest(section="Top Deals", max_results=5)
    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir, channel="chrome", headless=False, viewport=None,
            args=["--disable-blink-features=AutomationControlled", "--disable-infobars", "--disable-extensions"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = list_target_deals(page, request)
            assert result.section == request.section
            assert len(result.deals) <= request.max_results
            print(f"\nTotal deals found: {len(result.deals)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_list_target_deals)
