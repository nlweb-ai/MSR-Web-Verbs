"""
Auto-generated Playwright script (Python)
Costco Product Search: "kids winter jacket"

Generated on: 2026-02-26T19:32:18.266Z
Recorded 11 browser interactions
Note: This script was generated using AI-driven discovery patterns
"""

import re
import os
from playwright.sync_api import Page, sync_playwright, expect

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws, find_chrome_executable
import shutil

from dataclasses import dataclass
import subprocess
import tempfile
import json
import time
from urllib.request import urlopen

@dataclass(frozen=True)
class CostcoSearchRequest:
    search_query: str
    max_results: int

@dataclass(frozen=True)
class CostcoProduct:
    name: str
    price: str

@dataclass(frozen=True)
class CostcoSearchResult:
    search_query: str
    products: list[CostcoProduct]


# Searches Costco for products matching a query and returns up to max_results listings with name and price.
def search_costco_products(
    page: Page,
    request: CostcoSearchRequest,
) -> CostcoSearchResult:
    search_query = request.search_query
    max_results = request.max_results
    raw_results = []
    """
    Search Costco.com for the given query and return up to max_results items,
    each with name and price.
    """
    raw_results = []

    try:
        # Navigate to Costco
        page.goto("https://www.costco.com")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)

        # Find and fill the search box with multiple fallback strategies
        search_input = None
        search_selectors = [
            "input[placeholder*='Search']",
            "input[type='search']",
            "input[aria-label*='Search']",
            "input#search-field",
            "input[name*='search']",
            "input[id*='search']",
            "#search input",
            ".search input",
            "form input[type='text']"
        ]
        
        for selector in search_selectors:
            try:
                test_input = page.locator(selector).first
                if test_input.is_visible(timeout=2000):
                    search_input = test_input
                    print(f"Found search input with selector: {selector}")
                    break
            except Exception:
                continue
        
        if not search_input:
            print("DEBUG: Could not find search input. Page title:", page.title())
            print("DEBUG: Available input elements:")
            inputs = page.locator("input").all()
            for i, inp in enumerate(inputs[:5]):  # Show first 5 inputs
                try:
                    placeholder = inp.get_attribute("placeholder") or ""
                    input_type = inp.get_attribute("type") or ""
                    input_id = inp.get_attribute("id") or ""
                    print(f"  Input {i}: type='{input_type}' id='{input_id}' placeholder='{placeholder}'")
                except Exception:
                    pass
            raise Exception("Could not find search input element")
        
        search_input.evaluate("el => el.click()")
        search_input.fill(search_query)
        page.wait_for_timeout(500)

        # Click the Search button
        try:
            search_btn = page.get_by_role("button", name=re.compile(r"^Search$", re.IGNORECASE)).first
            search_btn.evaluate("el => el.click()")
        except Exception:
            search_input.press("Enter")

        # Wait for search raw_results to load
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)

        # Extract product listings from the raw_results page
        # Costco uses MUI and product links have '.product.' in href
        all_links = page.get_by_role("link").all()
        product_candidates = []
        seen_hrefs = set()
        for link in all_links:
            try:
                href = link.get_attribute("href", timeout=1000) or ""
                label = link.inner_text(timeout=1000).strip()
                # Product pages have '.product.' in the URL
                if ".product." in href and len(label) > 10 and href not in seen_hrefs:
                    seen_hrefs.add(href)
                    product_candidates.append({"element": link, "name": label, "href": href})
            except Exception:
                continue

        # For each product link, find the nearby price by walking up ancestor levels
        for candidate in product_candidates[:max_results]:
            name = candidate["name"]
            price = "N/A"
            try:
                el = candidate["element"]
                for level in range(1, 8):
                    xpath = "xpath=" + "/".join([".."] * level)
                    parent = el.locator(xpath)
                    if parent.count() == 0:
                        continue
                    parent_text = parent.first.inner_text(timeout=2000)
                    price_match = re.search(r"\$[\d,]+\.?\d*", parent_text)
                    if price_match:
                        price = price_match.group(0)
                        break
            except Exception:
                pass
            raw_results.append({"name": name, "price": price})

        if not raw_results:
            print("Warning: Could not find product listings.")

        # Print raw_results
        print(f"\nFound {len(raw_results)} raw_results for '{search_query}':\n")
        for i, item in enumerate(raw_results, 1):
            print(f"  {i}. {item['name']}")
            print(f"     Price: {item['price']}")

    except Exception as e:
        print(f"Error searching Costco: {e}")
    return CostcoSearchResult(
        search_query=search_query,
        products=[CostcoProduct(name=r["name"], price=r["price"]) for r in raw_results],
    )
def test_search_costco_products() -> None:
    from playwright.sync_api import sync_playwright
    request = CostcoSearchRequest(search_query="kids winter jacket", max_results=5)
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
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_costco_products(page, request)
        finally:
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)
    assert result.search_query == request.search_query
    assert len(result.products) <= request.max_results
    print(f"\nTotal products found: {len(result.products)}")


if __name__ == "__main__":
    test_search_costco_products()
