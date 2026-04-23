import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class NerdwalletCardsRequest:
    query: str = "cash back"
    max_results: int = 5


@dataclass(frozen=True)
class CreditCard:
    name: str = "N/A"
    category: str = "N/A"
    annual_fee: str = "N/A"
    rewards_rate: str = "N/A"
    intro_offer: str = "N/A"


@dataclass(frozen=True)
class NerdwalletCardsResult:
    cards: list = None
    query: str = ""


# Navigate to NerdWallet's best credit cards page for the given query category,
# extract up to max_results cards with name, category, annual fee, rewards rate,
# and sign-up bonus (intro offer), and return them as a list of CreditCard objects.
def nerdwallet_cards(page: Page, request: NerdwalletCardsRequest) -> NerdwalletCardsResult:
    print("  NerdWallet Credit Cards\n")

    slug = request.query.strip().lower().replace(" ", "-")
    url = f"https://www.nerdwallet.com/best/credit-cards/{slug}"

    checkpoint(f"Navigating to {url}")
    print(f"Loading {url}...")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    cards = []

    # Parse card listings
    # Pattern: 'Our pick for:' -> card name -> ... -> 'Annual fee' -> fee -> 'Rewards rate' -> rate -> 'Intro offer' -> bonus
    i = 0
    while i < len(text_lines) and len(cards) < request.max_results:
        line = text_lines[i]

        if line.startswith('Our pick for:'):
            category = line.replace('Our pick for: ', '')
            name = text_lines[i + 1] if i + 1 < len(text_lines) else 'N/A'

            annual_fee = 'N/A'
            rewards_rate = 'N/A'
            intro_offer = 'N/A'

            # Look ahead for details
            for j in range(i + 2, min(i + 30, len(text_lines))):
                jline = text_lines[j]
                if jline.startswith('Our pick for:'):
                    break
                if jline == 'Annual fee' and j + 1 < len(text_lines):
                    annual_fee = text_lines[j + 1]
                elif jline == 'Rewards rate' and j + 1 < len(text_lines):
                    rewards_rate = text_lines[j + 1]
                elif jline == 'Intro offer' and j + 1 < len(text_lines):
                    intro_offer = text_lines[j + 1]

            cards.append(CreditCard(
                name=name,
                category=category,
                annual_fee=annual_fee,
                rewards_rate=rewards_rate,
                intro_offer=intro_offer,
            ))

        i += 1

    print("=" * 60)
    print(f"NerdWallet: Best {request.query.title()} Credit Cards")
    print("=" * 60)
    for idx, c in enumerate(cards, 1):
        print(f"\n{idx}. {c.name}")
        print(f"   Category:    {c.category}")
        print(f"   Annual Fee:  {c.annual_fee}")
        print(f"   Rewards:     {c.rewards_rate}")
        print(f"   Sign-up:     {c.intro_offer}")

    print(f"\nFound {len(cards)} cards")

    return NerdwalletCardsResult(cards=cards, query=request.query)


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    with sync_playwright() as pw:
        chrome_profile = os.path.join(
            os.environ["USERPROFILE"],
            "AppData", "Local", "Google", "Chrome", "User Data", "Default",
        )
        context = pw.chromium.launch_persistent_context(
            chrome_profile,
            headless=False,
            channel="chrome",
        )
        page = context.pages[0] if context.pages else context.new_page()
        request = NerdwalletCardsRequest(query="cash back", max_results=5)
        result = nerdwallet_cards(page, request)
        print(f"\nReturned {len(result.cards)} cards for query '{result.query}'")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)