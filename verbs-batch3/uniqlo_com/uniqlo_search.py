import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class UniqloSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class UniqloProduct:
    name: str
    price: str
    colors: str


@dataclass(frozen=True)
class UniqloSearchResult:
    products: list  # list[UniqloProduct]


# Searches Uniqlo US for products matching a query and extracts product name,
# price, and available color count from the search results page.
def uniqlo_search(page: Page, request: UniqloSearchRequest) -> UniqloSearchResult:
    query = request.query
    max_results = request.max_results
    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    results = []

    # ── Navigate directly to search results ──────────────────────────
    query_encoded = query.replace(" ", "+")
    search_url = f"https://www.uniqlo.com/us/en/search?q={query_encoded}"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to page")
    page.goto(search_url, timeout=30000)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)

    # ── Dismiss modal overlay ─────────────────────────────────────────
    for selector in [
        'button[aria-label="Close"]',
        "button#onetrust-accept-btn-handler",
    ]:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=2000):
                checkpoint("Click element")
                btn.click()
                page.wait_for_timeout(500)
                break
        except Exception:
            pass

    # ── Wait for product cards ────────────────────────────────────────
    print("Waiting for product listings...")
    try:
        page.locator('a[class*="product"]').first.wait_for(
            state="visible", timeout=10000
        )
    except Exception:
        pass
    page.wait_for_timeout(2000)
    print(f"  Loaded: {page.url}")

    # ── Extract products ──────────────────────────────────────────────
    print(f"Extracting up to {max_results} products...")

    cards = page.locator('a[class*="product"]')
    count = cards.count()
    print(f"  Found {count} product cards on page")

    seen_names = set()
    for i in range(min(count, max_results * 3)):
        if len(results) >= max_results:
            break
        card = cards.nth(i)
        try:
            text = card.inner_text(timeout=3000)
            lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

            name = lines[1] if len(lines) > 1 else "N/A"

            # Deduplicate by name (same product appears for MEN and WOMEN)
            name_key = name.lower()
            if name_key in seen_names:
                continue
            seen_names.add(name_key)

            price = "N/A"
            for ln in lines:
                m = re.search(r"\$[\d,.]+", ln)
                if m:
                    price = m.group(0)
                    break

            # Count available colors from color chip images
            color_codes = card.evaluate("""e => {
                const imgs = e.querySelectorAll('img');
                return Array.from(imgs)
                    .map(i => i.alt)
                    .filter(a => /^\\d{2}$/.test(a));
            }""")
            num_colors = len(color_codes)
            colors_str = f"{num_colors} color{'s' if num_colors != 1 else ''}"

            if name == "N/A":
                continue

            results.append(UniqloProduct(
                name=name,
                price=price,
                colors=colors_str,
            ))
        except Exception:
            continue

    # ── Print results ─────────────────────────────────────────────────
    print(f'\nFound {len(results)} products for "{query}":\n')
    for i, p in enumerate(results, 1):
        print(f"  {i}. {p.name}")
        print(f"     Price: {p.price}  Colors: {p.colors}")
        print()

    return UniqloSearchResult(products=results)


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_profile = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default",
    )
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            chrome_profile,
            headless=False,
            channel="chrome",
        )
        page = context.pages[0] if context.pages else context.new_page()
        request = UniqloSearchRequest(query="ultra light down jacket", max_results=5)
        result = uniqlo_search(page, request)
        print(f"\nTotal products found: {len(result.products)}")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
