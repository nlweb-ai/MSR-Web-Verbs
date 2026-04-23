"""
Auto-generated Playwright script (Python)
Adopt-a-Pet – Adoptable Pet Search
Pet type: "dogs", Location: "Portland, OR"

Generated on: 2026-04-18T04:34:37.430Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class PetSearchRequest:
    pet_type: str = "dogs"
    location: str = "Portland, OR"
    max_results: int = 5


@dataclass
class Pet:
    name: str = ""
    breed: str = ""
    age: str = ""
    gender: str = ""
    shelter: str = ""


@dataclass
class PetSearchResult:
    pets: list = field(default_factory=list)


def adoptapet_search(page: Page, request: PetSearchRequest) -> PetSearchResult:
    """Search Adopt-a-Pet for adoptable pets."""
    print(f"  Pet type: {request.pet_type}")
    print(f"  Location: {request.location}\n")

    # ── Navigate ──────────────────────────────────────────────────────
    url = f"https://www.adoptapet.com/pet-search?pet_type={request.pet_type}&location={quote_plus(request.location)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Adopt-a-Pet search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Dismiss popups ────────────────────────────────────────────────
    for sel in [
        "button:has-text('Accept')",
        "button:has-text('Got it')",
        "button[aria-label='Close']",
        "#onetrust-accept-btn-handler",
    ]:
        try:
            btn = page.locator(sel).first
            if btn.is_visible(timeout=2000):
                btn.click()
                page.wait_for_timeout(500)
        except Exception:
            pass

    # ── Extract pets ──────────────────────────────────────────────────
    checkpoint("Extract pet listings")
    pets = page.evaluate(r"""(maxResults) => {
        const results = [];
        // Pet cards
        const cards = document.querySelectorAll(
            '.pet-card, [data-testid="pet-card"], .search-result-card, article'
        );
        for (const card of cards) {
            if (results.length >= maxResults) break;
            const text = card.innerText.trim();
            if (!text || text.length < 5) continue;

            const nameEl = card.querySelector('h2, h3, .pet-name, [data-testid="pet-name"]');
            const name = nameEl ? nameEl.innerText.trim() : '';

            // Look for breed, age, gender in the card text
            const lines = text.split('\n').map(l => l.trim()).filter(l => l);
            let breed = '', age = '', gender = '', shelter = '';

            for (const line of lines) {
                if (/puppy|kitten|adult|senior|young|baby/i.test(line) && !age) age = line;
                else if (/male|female/i.test(line) && !gender) gender = line;
                else if (/shelter|rescue|humane|spca|foster/i.test(line) && !shelter) shelter = line;
                else if (!breed && line !== name && line.length > 2 && line.length < 80) breed = line;
            }

            if (name) {
                results.push({ name, breed, age, gender, shelter });
            }
        }

        // Fallback: links with pet info
        if (results.length === 0) {
            const links = document.querySelectorAll('a[href*="/pet/"], a[href*="/dog/"], a[href*="/cat/"]');
            for (const link of links) {
                if (results.length >= maxResults) break;
                const text = link.innerText.trim();
                if (text && text.length > 2 && text.length < 100) {
                    results.push({ name: text, breed: '', age: '', gender: '', shelter: '' });
                }
            }
        }
        return results;
    }""", request.max_results)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Adopt-a-Pet: {request.pet_type} near {request.location}")
    print("=" * 60)
    for idx, p in enumerate(pets, 1):
        print(f"\n  {idx}. {p['name']}")
        print(f"     Breed: {p['breed']}")
        print(f"     Age: {p['age']}")
        print(f"     Gender: {p['gender']}")
        print(f"     Shelter: {p['shelter']}")

    result_pets = [Pet(**p) for p in pets]
    print(f"\nFound {len(result_pets)} pets")
    return PetSearchResult(pets=result_pets)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("adoptapet_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = adoptapet_search(page, PetSearchRequest())
            print(f"\nReturned {len(result.pets)} pets")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
