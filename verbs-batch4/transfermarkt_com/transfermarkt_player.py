import re
import os
from dataclasses import dataclass
from urllib.parse import quote as url_quote
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class TransfermarktPlayerRequest:
    player_name: str = "Kylian Mbappé"

@dataclass(frozen=True)
class TransfermarktPlayerResult:
    player_name: str = ""
    current_club: str = ""
    market_value: str = ""
    age: str = ""
    nationality: str = ""
    position: str = ""

# Search Transfermarkt for a soccer player by name
# and extract profile details including club, market value, age, nationality, and position.
def transfermarkt_player(page: Page, request: TransfermarktPlayerRequest) -> TransfermarktPlayerResult:
    player_name = request.player_name
    print(f"  Player: {player_name}\n")

    search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={url_quote(player_name)}"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to Transfermarkt search results")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    print(f"  Loaded: {page.url}")

    # Check for bot detection
    title = page.title().lower()
    body_start = (page.evaluate("document.body.innerText") or "")[:500].lower()
    if "blocked" in title or "403" in title or "captcha" in body_start or "bot" in title:
        print("  BLOCKED: Heavy bot-detection detected. Skipping.")
        return TransfermarktPlayerResult()

    # Accept cookies
    for selector in [
        'button:has-text("Accept All")',
        'button:has-text("Accept")',
        'button#onetrust-accept-btn-handler',
        '[title="Accept & continue"]',
    ]:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=2000):
                checkpoint(f"Accept cookies: {selector}")
                btn.click()
                page.wait_for_timeout(500)
                break
        except Exception:
            pass

    # Click first player result
    print("Clicking top player result...")
    checkpoint("Click on top player search result")
    player_link = page.locator(
        'table.items tbody tr td.hauptlink a, '
        '.spielerporträt a, '
        'a[href*="/profil/spieler/"]'
    ).first
    try:
        player_link.wait_for(state="visible", timeout=5000)
        player_link.click()
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)
        print(f"  Navigated to: {page.url}")
    except Exception as e:
        print(f"  Could not click player result: {e}")
        return TransfermarktPlayerResult()

    # Extract player profile data
    checkpoint("Extract player profile data")
    print("Extracting player info...")

    pname = "N/A"
    try:
        name_el = page.locator('h1[class*="data-header"], h1, [data-header-title]').first
        pname = name_el.inner_text(timeout=2000).strip()
    except Exception:
        pass

    market_value = "N/A"
    try:
        mv_el = page.locator(
            'a[class*="market-value"], '
            '[class*="market-value"], '
            '[class*="marktwert"]'
        ).first
        market_value = mv_el.inner_text(timeout=2000).strip()
    except Exception:
        pass

    body_text = page.evaluate("document.body.innerText") or ""

    current_club = "N/A"
    try:
        club_match = re.search(r"Current club[:\s]*([^\n]+)", body_text, re.IGNORECASE)
        if club_match:
            current_club = club_match.group(1).strip()
        else:
            club_el = page.locator('span[class*="info-table__content--bold"] a, [class*="hauptpunkt"] a').first
            current_club = club_el.inner_text(timeout=2000).strip()
    except Exception:
        pass

    position = "N/A"
    try:
        pos_match = re.search(r"Position[:\s]*([^\n]+)", body_text, re.IGNORECASE)
        if pos_match:
            position = pos_match.group(1).strip()
    except Exception:
        pass

    age = "N/A"
    try:
        age_match = re.search(r"(?:Date of birth/Age|Age)[:\s]*.*?(\d{1,2})\s*$", body_text, re.IGNORECASE | re.MULTILINE)
        if not age_match:
            age_match = re.search(r"\((\d{2})\)", body_text)
        if age_match:
            age = age_match.group(1)
    except Exception:
        pass

    nationality = "N/A"
    try:
        nat_match = re.search(r"Citizenship[:\s]*([^\n]+)", body_text, re.IGNORECASE)
        if not nat_match:
            nat_match = re.search(r"Nationality[:\s]*([^\n]+)", body_text, re.IGNORECASE)
        if nat_match:
            nationality = nat_match.group(1).strip()
    except Exception:
        pass

    result = TransfermarktPlayerResult(
        player_name=pname,
        current_club=current_club,
        market_value=market_value,
        age=age,
        nationality=nationality,
        position=position,
    )

    print("=" * 60)
    print(f"Transfermarkt - Player Profile")
    print("=" * 60)
    print(f"  Name: {result.player_name}")
    print(f"  Club: {result.current_club}")
    print(f"  Market Value: {result.market_value}")
    print(f"  Age: {result.age}")
    print(f"  Nationality: {result.nationality}")
    print(f"  Position: {result.position}")

    return result

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = transfermarkt_player(page, TransfermarktPlayerRequest())
        print(f"\nDone. Player: {result.player_name}")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
