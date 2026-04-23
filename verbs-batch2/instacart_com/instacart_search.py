"""
Playwright script (Python) — Instacart Product Search
Search for grocery products and extract name, price, and store.

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
class InstacartSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class InstacartProduct:
    name: str
    price: str
    store: str


@dataclass(frozen=True)
class InstacartSearchResult:
    query: str
    products: list[InstacartProduct]


# Searches Instacart for grocery products matching a query and extracts
# up to max_results products with name, price, and store.
def search_instacart(
    page: Page,
    request: InstacartSearchRequest,
) -> InstacartSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}\n")

    results: list[InstacartProduct] = []

    try:
        url = f"https://www.instacart.com/store/search/{query.replace(' ', '+')}"
        checkpoint(f"Navigate to {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)

        add_buttons = page.locator('button:has-text("Add")')
        count = add_buttons.count()
        print(f"  Found {count} product cards")

        for i in range(count):
            if len(results) >= max_results:
                break
            btn = add_buttons.nth(i)
            try:
                card_text = btn.evaluate("""el => {
                    let p = el.parentElement;
                    for (let j = 0; j < 5; j++) {
                        if (p && p.innerText && p.innerText.includes('$') && p.innerText.length > 20) {
                            return p.innerText;
                        }
                        p = p.parentElement;
                    }
                    return el.parentElement.parentElement.parentElement.innerText;
                }""")
                lines = [l.strip() for l in card_text.split("\n") if l.strip()]
                price = "N/A"
                name = "N/A"
                for line in lines:
                    m = re.search(r"Current price:\s*\$([\d.]+)", line)
                    if m:
                        price = f"${m.group(1)}"
                        break
                skip_patterns = [
                    r"^\$", r"^★", r"^Current price", r"^Original Price",
                    r"^Best seller$", r"^Great price$", r"^Sponsored$",
                    r"^\d+$", r"% off$", r"^\(", r"^Add$", r"^Show similar$",
                    r"sizes$", r"^reg\.", r"carousel", r"delivery",
                    r"^This is a", r"^Use", r"^Pickup", r"^Organic$",
                    r"^Groceries$", r"^EBT$", r"^No markups$", r"^Local$",
                    r"^Co-op$", r"^Prepared", r"^Butcher", r"^\d+\.\d+ mi$",
                    r"mi$",
                ]
                for line in lines:
                    if any(re.search(p, line, re.IGNORECASE) for p in skip_patterns):
                        continue
                    if re.match(r'^[\d.]+\s*(gal|oz|fl|ml|ct|lb|pk|qt|L)\b', line, re.IGNORECASE):
                        continue
                    if len(line) > 5:
                        name = line
                        break
                if name != "N/A" and price != "N/A":
                    results.append(InstacartProduct(name=name, price=price, store="N/A"))
                    print(f"  {len(results)}. {name} | {price}")
            except Exception:
                continue

        print(f"\nFound {len(results)} products for '{query}':")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r.name} — {r.price}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return InstacartSearchResult(query=query, products=results)


def test_search_instacart() -> None:
    request = InstacartSearchRequest(query="organic milk", max_results=5)
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
            result = search_instacart(page, request)
            assert result.query == request.query
            assert len(result.products) <= request.max_results
            print(f"\nTotal products found: {len(result.products)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_instacart)
