import re
import os
from dataclasses import dataclass
from urllib.parse import quote
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


CURRENT_PRICE_RE = re.compile(r'^current price \$(\S+)')
UNIT_PRICE_RE = re.compile(r'^\$[\d.]+/\w+')
RATING_RE = re.compile(r'^([\d.]+) out of 5 Stars\. (\d+) reviews?')


@dataclass(frozen=True)
class SamsclubSearchRequest:
    query: str = "protein bars"
    max_results: int = 5


@dataclass(frozen=True)
class SamsclubProduct:
    name: str = ""
    price: str = "N/A"
    unit_price: str = "N/A"
    rating: str = "N/A"


@dataclass(frozen=True)
class SamsclubSearchResult:
    products: tuple = ()


# Search for products on samsclub.com by query and extract listings
# including product name, price, unit price, and rating.
def samsclub_search(page: Page, request: SamsclubSearchRequest) -> SamsclubSearchResult:
    print(f"  Query: {request.query}\n")

    url = f"https://www.samsclub.com/s/{quote(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Skip to search results (after 'Relevance' sort option)
    i = 0
    while i < len(text_lines):
        if text_lines[i] == 'Relevance':
            i += 1
            break
        i += 1

    # Skip 'Related searches' section
    if i < len(text_lines) and text_lines[i] == 'Related searches':
        while i < len(text_lines) and text_lines[i] != 'Add to Cart':
            i += 1

    results = []
    seen = set()
    while i < len(text_lines) and len(results) < request.max_results:
        line = text_lines[i]

        if line == 'Add to Cart' and i > 0:
            name = text_lines[i - 1]
            if name in seen:
                i += 1
                continue
            seen.add(name)

            # Scan forward for price, unit price, rating
            price = 'N/A'
            unit_price = 'N/A'
            rating = 'N/A'

            for j in range(i + 1, min(i + 10, len(text_lines))):
                cm = CURRENT_PRICE_RE.match(text_lines[j])
                if cm:
                    price = '$' + cm.group(1)
                if UNIT_PRICE_RE.match(text_lines[j]):
                    unit_price = text_lines[j]
                rm = RATING_RE.match(text_lines[j])
                if rm:
                    rating = f"{rm.group(1)}/5 ({rm.group(2)} reviews)"
                    break

            results.append(SamsclubProduct(
                name=name,
                price=price,
                unit_price=unit_price,
                rating=rating,
            ))

        i += 1

    print("=" * 60)
    print(f"Sam's Club: {request.query}")
    print("=" * 60)
    for idx, r in enumerate(results, 1):
        print(f"\n{idx}. {r.name}")
        print(f"   Price:      {r.price}")
        print(f"   Unit Price: {r.unit_price}")
        print(f"   Rating:     {r.rating}")

    print(f"\nFound {len(results)} products")

    return SamsclubSearchResult(products=tuple(results))


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
        request = SamsclubSearchRequest()
        result = samsclub_search(page, request)
        print(f"\nReturned {len(result.products)} products")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)