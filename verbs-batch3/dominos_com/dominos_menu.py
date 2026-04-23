"""
Playwright script (Python) — Domino's Pizza Menu Extraction
Location: New York, NY 10001

Navigates to the Domino's specialty pizza menu page to extract pizza names
and descriptions, then uses the Domino's public API for prices and sizes.
Uses the user's Chrome profile for persistent login state.
"""

import re
import json
import os
from urllib.request import urlopen, Request
from urllib.parse import quote
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


STORE_LOCATOR_API = "https://order.dominos.com/power/store-locator"
MENU_API_BASE = "https://order.dominos.com/power/store"
MENU_URL = "https://www.dominos.com/menu/specialty"


@dataclass(frozen=True)
class DominosMenuRequest:
    location: str
    max_results: int


@dataclass(frozen=True)
class DominosPizza:
    name: str
    description: str
    sizes: tuple[str, ...]
    starting_price: str


@dataclass(frozen=True)
class DominosMenuResult:
    location: str
    store_id: str
    pizzas: list[DominosPizza]


# Navigates to the Domino's specialty pizza menu page, extracts pizza names/descriptions,
# and fetches prices from the Domino's API for the nearest store to the given location.
def get_dominos_menu(
    page: Page,
    request: DominosMenuRequest,
) -> DominosMenuResult:
    location = request.location
    max_results = request.max_results

    print(f"  Location: {location}")
    print(f"  Max results: {max_results}\n")

    results: list[DominosPizza] = []
    store_id = "N/A"

    try:
        # ── Navigate to specialty pizzas page ─────────────────────────
        print("Loading Domino's specialty pizza menu...")
        checkpoint(f"Navigate to {MENU_URL}")
        page.goto(MENU_URL)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(8000)
        print(f"  Loaded: {page.url}")

        # ── Extract pizza names and descriptions from page ────────────
        text = page.evaluate("document.body ? document.body.innerText : ''") or ""
        text_lines = [l.strip() for l in text.split("\n") if l.strip()]

        pizza_names = []
        in_section = False
        i = 0
        while i < len(text_lines):
            line = text_lines[i]
            if line == "SPECIALTY PIZZAS" and not in_section:
                if i + 1 < len(text_lines) and text_lines[i + 1] in ("START YOUR ORDER", "DELIVERY"):
                    in_section = True
                    i += 1
                    continue
            if in_section:
                if line in ("FULL MENU", "BUILD YOUR OWN"):
                    break
                if line not in ("START YOUR ORDER", "DELIVERY", "OR", "CARRYOUT",
                                "NEW!", "TRENDING") and not line.startswith("Customize "):
                    if len(line) < 40 and "." not in line and "," not in line:
                        desc = ""
                        if i + 1 < len(text_lines):
                            next_line = text_lines[i + 1]
                            if len(next_line) > 40 or "," in next_line:
                                desc = next_line
                        pizza_names.append({"name": line, "description": desc})
            i += 1

        print(f"\nFound {len(pizza_names)} specialty pizzas on page")

        # ── Get prices from Domino's API ──────────────────────────────
        print("\nFetching store and price data from Domino's API...")

        store_url = f"{STORE_LOCATOR_API}?s={quote(location)}&type=Carryout"
        req = Request(store_url, headers={"User-Agent": "Mozilla/5.0"})
        store_data = json.loads(urlopen(req, timeout=10).read().decode())
        stores = store_data.get("Stores", [])
        if not stores:
            print("  No stores found for location:", location)
            return DominosMenuResult(location=location, store_id="N/A", pizzas=[])

        store_id = stores[0]["StoreID"]
        store_addr = stores[0].get("AddressDescription", "").split("\n")[0]
        print(f"  Using store: #{store_id} ({store_addr})")

        menu_url = f"{MENU_API_BASE}/{store_id}/menu?lang=en&structured=true"
        req = Request(menu_url, headers={"User-Agent": "Mozilla/5.0"})
        menu_data = json.loads(urlopen(req, timeout=15).read().decode())
        products = menu_data.get("Products", {})
        variants = menu_data.get("Variants", {})

        api_pizzas = {}
        for code, prod in products.items():
            if prod.get("ProductType") == "Pizza" and code != "S_PIZZA":
                api_pizzas[prod["Name"]] = {"code": code, "product": prod}

        for pizza in pizza_names[:max_results]:
            name = pizza["name"]
            desc = pizza["description"]

            api_match = api_pizzas.get(name)
            sizes = []
            starting_price = "N/A"

            if api_match:
                prod = api_match["product"]
                variant_codes = prod.get("Variants", [])
                size_prices = {}
                for vc in variant_codes:
                    v = variants.get(vc)
                    if v:
                        size_code = v.get("SizeCode", "")
                        price = float(v.get("Price", "0"))
                        if size_code == "10":
                            label = 'Small (10")'
                        elif size_code == "12":
                            label = 'Medium (12")'
                        elif size_code == "14":
                            label = 'Large (14")'
                        elif size_code == "16":
                            label = 'X-Large (16")'
                        else:
                            label = size_code
                        if label not in size_prices or price < size_prices[label]:
                            size_prices[label] = price

                sizes = sorted(size_prices.items(), key=lambda x: x[1])
                if sizes:
                    starting_price = "$" + f"{sizes[0][1]:.2f}"

            results.append(DominosPizza(
                name=name,
                description=desc[:80] + "..." if len(desc) > 80 else desc,
                sizes=tuple("$" + f"{s[1]:.2f}" + " " + s[0] for s in sizes),
                starting_price=starting_price,
            ))

        # ── Print results ─────────────────────────────────────────────
        print()
        print("=" * 60)
        print(f"Domino's Specialty Pizzas (Store #{store_id})")
        print("=" * 60)
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r.name}")
            if r.description:
                print(f"   {r.description}")
            print(f"   Starting price: {r.starting_price}")
            if r.sizes:
                print(f"   Sizes: {', '.join(r.sizes)}")

        print(f"\nFound {len(results)} pizzas")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    return DominosMenuResult(
        location=location,
        store_id=store_id,
        pizzas=results,
    )


def test_get_dominos_menu() -> None:
    request = DominosMenuRequest(
        location="New York, NY 10001",
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
            result = get_dominos_menu(page, request)
            assert result.location == request.location
            assert len(result.pizzas) <= request.max_results
            print(f"\nTotal pizzas found: {len(result.pizzas)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_get_dominos_menu)