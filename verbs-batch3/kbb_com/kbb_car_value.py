import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


PRICE_RE = re.compile(r'^\$[\d,]+$')
CONDITIONS = ['Excellent', 'Very Good', 'Good', 'Fair']


@dataclass(frozen=True)
class KbbCarValueRequest:
    make: str = "toyota"
    model: str = "camry"
    year: str = "2020"
    trim: str = "se"
    body_style: str = "sedan-4d"


@dataclass(frozen=True)
class ConditionValues:
    excellent: str = "N/A"
    very_good: str = "N/A"
    good: str = "N/A"
    fair: str = "N/A"


@dataclass(frozen=True)
class KbbCarValueResult:
    vehicle: str = ""
    fair_purchase_price: str = "N/A"
    trade_in: ConditionValues = None
    private_party: ConditionValues = None


# Navigate to KBB and look up the value/pricing for a given vehicle year/make/model/trim.
# Extracts fair purchase price, trade-in values, and private party values by condition.
def kbb_car_value(page: Page, request: KbbCarValueRequest) -> KbbCarValueResult:
    make = request.make
    model = request.model
    year = request.year
    trim = request.trim
    body_style = request.body_style
    print(f"  Vehicle: {year} {make.title()} {model.title()} {trim.upper()}")

    url = f"https://www.kbb.com/{make}/{model}/{year}/{trim}-{body_style}/"
    print(f"Loading {url}...")
    checkpoint("Navigate to page")
    page.goto(url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(10000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    fair_price = None
    trade_in = {}
    private_party = {}

    i = 0
    while i < len(text_lines):
        line = text_lines[i]

        if line == "Fair Purchase Price" and i + 1 < len(text_lines):
            nxt = text_lines[i + 1]
            if PRICE_RE.match(nxt) and not fair_price:
                fair_price = nxt
                i += 2
                continue

        if line in CONDITIONS:
            cond = line
            if i + 2 < len(text_lines):
                ti = text_lines[i + 1]
                pp = text_lines[i + 2]
                if PRICE_RE.match(ti) and PRICE_RE.match(pp):
                    trade_in[cond] = ti
                    private_party[cond] = pp
                    i += 3
                    continue

        i += 1

    title = f"{year} {make.title()} {model.title()} {trim.upper()}"
    print("=" * 60)
    print(f"KBB Values for {title}")
    print("=" * 60)
    print(f"\nFair Purchase Price: {fair_price or 'N/A'}")
    print(f"\nTrade-In Values:")
    for cond in CONDITIONS:
        print(f"  {cond:>10}: {trade_in.get(cond, 'N/A')}")
    print(f"\nPrivate Party Values:")
    for cond in CONDITIONS:
        print(f"  {cond:>10}: {private_party.get(cond, 'N/A')}")

    trade_in_values = ConditionValues(
        excellent=trade_in.get("Excellent", "N/A"),
        very_good=trade_in.get("Very Good", "N/A"),
        good=trade_in.get("Good", "N/A"),
        fair=trade_in.get("Fair", "N/A"),
    )
    private_party_values = ConditionValues(
        excellent=private_party.get("Excellent", "N/A"),
        very_good=private_party.get("Very Good", "N/A"),
        good=private_party.get("Good", "N/A"),
        fair=private_party.get("Fair", "N/A"),
    )

    return KbbCarValueResult(
        vehicle=title,
        fair_purchase_price=fair_price or "N/A",
        trade_in=trade_in_values,
        private_party=private_party_values,
    )


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_user_data = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            chrome_user_data,
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        result = kbb_car_value(page, KbbCarValueRequest())
        print(f"\nResult: {result}")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)