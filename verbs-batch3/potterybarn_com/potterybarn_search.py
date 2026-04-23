import re
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


PRICE_RE = re.compile(r'^\$\s+[\d,]+')
COLORS_RE = re.compile(r'^\+\s+(\d+)\s+more$')


@dataclass(frozen=True)
class PotteryBarnSearchRequest:
    query: str = "sofa"
    max_results: int = 5


@dataclass(frozen=True)
class PotteryBarnProduct:
    name: str = ""
    price: str = ""
    colors: str = ""


@dataclass(frozen=True)
class PotteryBarnSearchResult:
    products: tuple = ()


# Search for products on potterybarn.com by query and extract listings with name, price, and available colors.
def potterybarn_search(page: Page, request: PotteryBarnSearchRequest) -> PotteryBarnSearchResult:
    print(f"  Query: {request.query}\n")

    url = f"https://www.potterybarn.com/search/results.html?words={quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(10000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    results = []

    # Skip to search results
    i = 0
    while i < len(text_lines):
        if text_lines[i] == 'Best Match':
            i += 1
            break
        i += 1

    while i < len(text_lines) and len(results) < request.max_results:
        line = text_lines[i]

        if line == 'Contract Grade':
            # Product name is the next line
            name = text_lines[i + 1] if i + 1 < len(text_lines) else 'Unknown'

            # Find price (look ahead up to 6 lines)
            price = 'N/A'
            for j in range(i + 2, min(i + 8, len(text_lines))):
                if PRICE_RE.match(text_lines[j]):
                    price = text_lines[j]
                    break

            # Find colors (look back for '+ N more')
            colors = 'N/A'
            for j in range(i - 1, max(i - 6, 0), -1):
                cm = COLORS_RE.match(text_lines[j])
                if cm:
                    colors = cm.group(1) + '+ colors'
                    break

            results.append(PotteryBarnProduct(
                name=name,
                price=price,
                colors=colors,
            ))

        i += 1

    print("=" * 60)
    print(f"Pottery Barn: {request.query}")
    print("=" * 60)
    for idx, r in enumerate(results, 1):
        print(f"\n{idx}. {r.name}")
        print(f"   Price:  {r.price}")
        print(f"   Colors: {r.colors}")

    print(f"\nFound {len(results)} products")

    return PotteryBarnSearchResult(products=tuple(results))


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_user_data = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default")
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            user_data_dir=os.path.join(chrome_user_data, "Default"),
            headless=False,
            channel="chrome",
        )
        page = context.pages[0] if context.pages else context.new_page()
        result = potterybarn_search(page, PotteryBarnSearchRequest())
        print(f"\nReturned {len(result.products)} products")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)