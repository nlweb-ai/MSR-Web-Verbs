"""
Uber Eats – Sushi Restaurants in Seattle, WA
Pure Playwright – no AI.
"""
import re, os, sys, traceback, shutil
from playwright.sync_api import Page, sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws, find_chrome_executable

from dataclasses import dataclass
import subprocess
import tempfile
import json
import time
from urllib.request import urlopen


ADDRESS = "Seattle, WA 98101"
QUERY = "sushi"


@dataclass(frozen=True)
class UberEatsSearchRequest:
    address: str = "Seattle, WA 98101"
    query: str = "sushi"
    max_results: int = 5


@dataclass(frozen=True)
class UberEatsRestaurant:
    name: str
    rating: str
    delivery_fee: str
    est_time: str


@dataclass(frozen=True)
class UberEatsSearchResult:
    address: str
    query: str
    restaurants: list


def search_ubereats_restaurants(page: Page, request: UberEatsSearchRequest) -> UberEatsSearchResult:
    restaurants = []
    try:
        print("STEP 1: Navigate to Uber Eats and set address...")
        checkpoint("Navigate to Uber Eats homepage")
        page.goto("https://www.ubereats.com/", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(5000)

        # Dismiss popups
        for sel in ["button:has-text('Accept')", "button:has-text('Got It')",
                     "[aria-label='Close']", "#onetrust-accept-btn-handler"]:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=800):
                    checkpoint(f"Dismiss popup: {sel}")
                    loc.evaluate("el => el.click()")
                    page.wait_for_timeout(400)
            except Exception:
                pass

        # Enter delivery address
        address_entered = False
        addr_sels = [
            "input[data-testid='address-input']",
            "input[placeholder*='address']",
            "input[aria-label*='address']",
            "input[aria-label*='delivery']",
            "input[placeholder*='Enter delivery address']",
            "input[id*='location']",
        ]
        for asel in addr_sels:
            if address_entered:
                break
            try:
                inp = page.locator(asel).first
                if inp.is_visible(timeout=1500):
                    checkpoint("Click address input field")
                    inp.click()
                    page.wait_for_timeout(500)
                    checkpoint("Fill delivery address")
                    inp.fill(ADDRESS)
                    page.wait_for_timeout(2500)
                    # Click first suggestion
                    sug_sels = [
                        "li[role='option']",
                        "[data-testid*='suggestion']",
                        "[class*='suggestion']",
                        "[class*='Suggestion']",
                        "[role='listbox'] li",
                        "[class*='AddressSuggestion']",
                    ]
                    for sug in sug_sels:
                        try:
                            sl = page.locator(sug).first
                            if sl.is_visible(timeout=1500):
                                checkpoint("Click address suggestion")
                                sl.evaluate("el => el.click()")
                                address_entered = True
                                page.wait_for_timeout(3000)
                                break
                        except Exception:
                            continue
            except Exception:
                continue

        if not address_entered:
            print("   Could not enter address via input — trying direct URL with place ID...")
            # Try with a known place ID for Seattle
            checkpoint("Navigate to Uber Eats with Seattle place ID")
            page.goto(
                "https://www.ubereats.com/feed?diningMode=DELIVERY&pl=JTdCJTIyYWRkcmVzcyUyMiUzQSUyMlNlYXR0bGUlMkMlMjBXQSUyMiU3RA%3D%3D",
                wait_until="domcontentloaded", timeout=30000,
            )
            page.wait_for_timeout(5000)

        # Now search
        print("STEP 1b: Search for sushi...")
        search_entered = False
        search_sels = [
            "input[placeholder*='Search']",
            "input[aria-label*='Search']",
            "input[data-testid*='search']",
            "[class*='SearchBar'] input",
        ]
        for ssel in search_sels:
            if search_entered:
                break
            try:
                sinp = page.locator(ssel).first
                if sinp.is_visible(timeout=2000):
                    checkpoint("Click search input")
                    sinp.click()
                    page.wait_for_timeout(500)
                    checkpoint("Fill search query")
                    sinp.fill(QUERY)
                    page.wait_for_timeout(1000)
                    checkpoint("Press Enter to search")
                    page.keyboard.press("Enter")
                    search_entered = True
                    page.wait_for_timeout(5000)
            except Exception:
                continue

        if not search_entered:
            # Navigate directly to search URL — it might work now that address is set
            checkpoint("Navigate directly to search URL")
            page.goto(f"https://www.ubereats.com/search?q={QUERY}",
                       wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)

        # Scroll to load content
        for _ in range(6):
            checkpoint("Scroll down to load more content")
            page.evaluate("window.scrollBy(0, 600)")
            page.wait_for_timeout(800)

        print("STEP 2: Extract restaurant data...")

        # ── Strategy 1: restaurant card selectors ──
        seen = set()
        card_sels = [
            "[data-testid*='store-card']",
            "[data-testid*='restaurant']",
            "a[href*='/store/']",
            "[class*='StoreCard']",
            "[class*='store-card']",
        ]
        for sel in card_sels:
            if len(restaurants) >= request.max_results:
                break
            try:
                cards = page.locator(sel).all()
                if not cards:
                    continue
                print(f"   Selector '{sel}' → {len(cards)} elements")
                for card in cards:
                    if len(restaurants) >= request.max_results:
                        break
                    try:
                        text = card.inner_text(timeout=2000).strip()
                        lines = [l.strip() for l in text.splitlines() if l.strip()]
                        if len(lines) < 2:
                            continue

                        name = ""
                        rating = "N/A"
                        delivery_fee = "N/A"
                        est_time = "N/A"

                        for ln in lines:
                            # Restaurant name: first line that's long enough, not a price/number
                            if not name and len(ln) > 3 and len(ln) < 80 and not re.match(r"^[\$\d\.\+]", ln):
                                if not re.search(r"^\d+\.?\d*$|^Free|^Delivery|^min$|^rating", ln, re.IGNORECASE):
                                    name = ln
                            # Rating: "4.7" or "4.7 (200+)"
                            if re.match(r"^\d\.\d", ln) and len(ln) < 30:
                                rating = ln
                            # Delivery fee: "$0.49 Delivery Fee" or "Free Delivery"
                            if re.search(r"\$[\d.]+\s*Delivery|Free\s*Delivery|\$[\d.]+\s*Fee", ln, re.IGNORECASE):
                                delivery_fee = ln[:40]
                            elif "$" in ln and "delivery" in ln.lower():
                                delivery_fee = ln[:40]
                            # Est time: "15–25 min"
                            if re.search(r"\d+[–\-]\d+\s*min|\d+\s*min", ln, re.IGNORECASE) and len(ln) < 30:
                                est_time = ln

                        if name:
                            key = name.lower()
                            if key not in seen:
                                seen.add(key)
                                restaurants.append({
                                    "name": name,
                                    "rating": rating,
                                    "delivery_fee": delivery_fee,
                                    "est_time": est_time,
                                })
                    except Exception:
                        continue
            except Exception:
                continue

        # ── Strategy 2: body text parsing ──
        if not restaurants:
            print("   Strategy 1 found 0 – trying body text...")
            body = page.inner_text("body")
            lines = [l.strip() for l in body.splitlines() if l.strip()]
            i = 0
            while i < len(lines) and len(restaurants) < request.max_results:
                ln = lines[i]
                # Look for restaurant-like names followed by rating/delivery info
                if (len(ln) > 5 and len(ln) < 80
                    and not re.search(r"sign|log in|cart|order|uber|address|deliver to|search", ln, re.IGNORECASE)
                    and not re.match(r"^[\$\d]", ln)):
                    # Check if next lines have rating/time/fee pattern
                    context_lines = lines[i+1:i+6]
                    has_rating = any(re.match(r"^\d\.\d", cl) for cl in context_lines)
                    has_time = any(re.search(r"\d+.*min", cl, re.IGNORECASE) for cl in context_lines)
                    has_fee = any("$" in cl or "delivery" in cl.lower() for cl in context_lines)

                    if has_rating or (has_time and has_fee):
                        name = ln
                        key = name.lower()
                        if key not in seen:
                            seen.add(key)
                            rating = "N/A"
                            delivery_fee = "N/A"
                            est_time = "N/A"
                            for cl in context_lines:
                                if re.match(r"^\d\.\d", cl) and rating == "N/A":
                                    rating = cl[:30]
                                if re.search(r"\d+[–\-]\d+\s*min|\d+\s*min", cl) and est_time == "N/A":
                                    est_time = cl[:30]
                                if re.search(r"\$[\d.]+.*(?:delivery|fee)|free\s*delivery", cl, re.IGNORECASE) and delivery_fee == "N/A":
                                    delivery_fee = cl[:40]
                            restaurants.append({
                                "name": name,
                                "rating": rating,
                                "delivery_fee": delivery_fee,
                                "est_time": est_time,
                            })
                i += 1

        if not restaurants:
            body = page.inner_text("body")
            if not body.strip():
                print("❌ ERROR: Page body is empty — possible bot protection.")
            else:
                print("❌ ERROR: Extraction failed — no restaurants found.")

        print(f"\nDONE – Top {len(restaurants)} Sushi Restaurants:")
        for i, r in enumerate(restaurants, 1):
            print(f"  {i}. {r['name']} | ★{r['rating']} | Fee: {r['delivery_fee']} | {r['est_time']}")

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    return UberEatsSearchResult(
        address=request.address,
        query=request.query,
        restaurants=[UberEatsRestaurant(name=r['name'], rating=r['rating'],
                                        delivery_fee=r['delivery_fee'], est_time=r['est_time']) for r in restaurants],
    )


def test_ubereats_restaurants():
    from playwright.sync_api import sync_playwright
    request = UberEatsSearchRequest(address="Seattle, WA 98101", query="sushi", max_results=5)
    port = get_free_port()
    profile_dir = tempfile.mkdtemp(prefix="chrome_cdp_")
    chrome = os.environ.get("CHROME_PATH") or find_chrome_executable()
    chrome_proc = subprocess.Popen(
        [
            chrome,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={profile_dir}",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1280,987",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    ws_url = None
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            resp = urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2)
            ws_url = json.loads(resp.read()).get("webSocketDebuggerUrl", "")
            if ws_url:
                break
        except Exception:
            pass
        time.sleep(0.4)
    if not ws_url:
        raise TimeoutError("Chrome CDP not ready")
    with sync_playwright() as pl:
        browser = pl.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_ubereats_restaurants(page, request)
        finally:
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)
    print(f"\nTotal restaurants: {len(result.restaurants)}")
    for i, r in enumerate(result.restaurants, 1):
        print(f"  {i}. {r.name}  {r.rating}  {r.delivery_fee}")


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_ubereats_restaurants)