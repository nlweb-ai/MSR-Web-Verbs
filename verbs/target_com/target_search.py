#!/usr/bin/env python3

from dataclasses import dataclass

"""Target coffee maker search – Playwright (auto-generated)."""

import json, re, subprocess, tempfile, shutil, os, sys, time
from pathlib import Path
from playwright.sync_api import Page, sync_playwright, TimeoutError as PWTimeout

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws, find_chrome_executable
from playwright_debugger import checkpoint
from urllib.request import urlopen

QUERY   = "coffee maker"
MAX     = 5

REFERENCE = json.loads(r"""
[
  {
    "name": "Ninja DualBrew Hot & Iced Coffee Maker -CFP101: 12-Cup, Custom Brew Strength, Removable Reservoir, Glass Carafe",
    "price": "",
    "rating": "N/A"
  },
  {
    "name": "Ninja Single-Serve Pods & Grounds Coffee Maker with Integrated Milk Frother",
    "price": "",
    "rating": "N/A"
  },
  {
    "name": "Fellow Aiden Precision Coffee Maker Matte Black",
    "price": "",
    "rating": "N/A"
  },
  {
    "name": "Mr. Coffee 12-Cup Switch Coffee Maker Black: Electric Drip Coffee Machine, 60 oz Capacity, Dishwasher-Safe Parts",
    "price": "",
    "rating": "N/A"
  },
  {
    "name": "Hamilton Beach 12 Cup Programmable Coffee Maker Black 46290: Drip Coffee Machine, Nonstick Hot Plate, Brew Pause",
    "price": "",
    "rating": "N/A"
  }
]
""")

def dismiss(page):
    for sel in [
        "#onetrust-accept-btn-handler",
        "button.onetrust-close-btn-handler",
        "button:has-text('Accept All')",
        "button:has-text('Accept')",
        "button:has-text('Got it')",
        "button:has-text('OK')",
        "button:has-text('Dismiss')",
        "button:has-text('Close')",
    ]:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=600):
                checkpoint(f"dismiss: clicking {sel}")
                loc.evaluate("el => el.click()")
                time.sleep(0.3)
        except Exception:
            pass

# ── main ─────────────────────────────────────────────────
@dataclass(frozen=True)
class TargetSearchRequest:
    search_query: str = "coffee maker"
    max_results: int = 5


@dataclass(frozen=True)
class TargetProduct:
    name: str
    price: str
    rating: str


@dataclass(frozen=True)
class TargetSearchResult:
    search_query: str
    products: list


def search_target_products(page: Page, request: TargetSearchRequest) -> TargetSearchResult:
    url = f"https://www.target.com/s?searchTerm={request.search_query.replace(' ', '+')}"
    checkpoint(f"navigating to Target search: {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(4000)
    dismiss(page)

    # Try to apply rating filter via AI-like approach: click the rating filter
    try:
        rating_filter = page.locator("text=/4 stars? & up|4\\+|Guest [Rr]ating 4/i").first
        if rating_filter.is_visible(timeout=3000):
            checkpoint("clicking rating filter")
            rating_filter.evaluate("el => el.click()")
            page.wait_for_timeout(2000)
    except Exception:
        pass

    # Extract via product card selectors (more reliable than raw text parsing)
    products = []

    # Target uses data-test="@web/ProductCard/title" for product title links
    TITLE_SELECTORS = [
        '[data-test="@web/ProductCard/title"]',
        '[data-test*="ProductCard/title"]',
    ]

    cards_found = False
    for title_sel in TITLE_SELECTORS:
        titles = page.locator(title_sel)
        count = titles.count()
        if count > 0:
            cards_found = True
            for idx in range(min(count, request.max_results)):
                el = titles.nth(idx)
                name = el.inner_text().strip()
                if not name:
                    continue

                # Walk up to the product card container to find price/rating nearby
                card = el.evaluate("""el => {
                    let node = el;
                    for (let i = 0; i < 8; i++) {
                        node = node.parentElement;
                        if (!node) return null;
                        if (node.querySelector('[data-test="product-details"]') ||
                            node.querySelector('[data-test="current-price"]') ||
                            node.textContent.match(/\\$\\d+/))
                            return node.outerHTML;
                    }
                    return node ? node.outerHTML : null;
                }""")

                price_str = ""
                rating = "N/A"
                if card:
                    pm = re.search(r'\$(\d+(?:\.\d{2})?)', card)
                    if pm:
                        price_str = "$" + pm.group(1)
                    rm = re.search(r'(\d+\.\d)\s*out of\s*5', card)
                    if rm:
                        rating = rm.group(1)

                if not any(p["name"] == name for p in products):
                    products.append({"name": name, "price": price_str, "rating": rating})
            break  # stop after first working selector

    # Fallback: text-based extraction with stricter filtering
    if not cards_found:
        SKIP_PATTERNS = re.compile(
            r'^(Same.day Delivery|Highly rated|Shipping dates may vary|Free shipping'
            r'|Pick it up|In stock|Only at Target|Clearance|Sale|New|Best seller'
            r'|Not available|Out of stock|Limited stock|Add to cart|Shop|Pickup'
            r'|Delivery|Shipping|Sign in|Create account|Registry|Weekly Ad'
            r'|Target Circle|Redcard|Gift Cards|Find a Store|Orders|get it)',
            re.IGNORECASE,
        )
        text = page.inner_text("body")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        i = 0
        while i < len(lines) and len(products) < request.max_results:
            line = lines[i]
            price_match = re.match(r'^\$(\d+(?:\.\d{2})?)', line)
            if price_match and i > 0:
                name = None
                for back in range(i - 1, max(i - 5, -1), -1):
                    candidate = lines[back]
                    if (len(candidate) > 15
                        and not candidate.startswith('$')
                        and not re.match(r'^\d+(\.\d)?\s*out of', candidate)
                        and 'Sponsored' not in candidate
                        and not candidate.startswith('Save ')
                        and not SKIP_PATTERNS.match(candidate)):
                        name = candidate
                        break
                if not name:
                    i += 1
                    continue
                price_str = "$" + price_match.group(1)
                rating = "N/A"
                for near in range(max(i - 3, 0), min(i + 5, len(lines))):
                    rm = re.search(r'(\d+\.\d)\s*out of\s*5', lines[near])
                    if rm:
                        rating = rm.group(1)
                        break
                if not any(p["name"] == name for p in products):
                    products.append({"name": name, "price": price_str, "rating": rating})
            i += 1

    print()
    print("=" * 60)
    print(f"  Target – Top {request.max_results} '{request.search_query}'")
    print("=" * 60)
    for idx, p in enumerate(products, 1):
        print(f"  {idx}. {p['name']}")
        print(f"     Price:  {p['price']}")
        print(f"     Rating: {p['rating']}")
        print()

    if not products:
        print("  ⚠ No products extracted from page text.")
        print("  Reference results from JS run:")
        for idx, r in enumerate(REFERENCE, 1):
            print(f"  {idx}. {r.get('name','?')} – {r.get('price','?')} – Rating: {r.get('rating','?')}")

    return TargetSearchResult(
        search_query=request.search_query,
        products=[TargetProduct(name=p['name'], price=p['price'], rating=p['rating']) for p in products],
    )


def test_target_products():
    from playwright.sync_api import sync_playwright
    request = TargetSearchRequest(search_query='coffee maker', max_results=5)
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
            result = search_target_products(page, request)
        finally:
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)
    print(f'\nTotal products: {len(result.products)}')
    for i, p in enumerate(result.products, 1):
        print(f'  {i}. {p.name}  {p.price}')


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_target_products)
