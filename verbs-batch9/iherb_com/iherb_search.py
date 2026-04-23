"""
Playwright script (Python) — iHerb Product Search
Search iHerb for supplements and health products.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class IHerbRequest:
    search_query: str = "vitamin D supplements"
    max_results: int = 5


@dataclass
class ProductItem:
    name: str = ""
    brand: str = ""
    price: str = ""
    dosage: str = ""
    servings: str = ""
    rating: str = ""


@dataclass
class IHerbResult:
    query: str = ""
    items: List[ProductItem] = field(default_factory=list)


def search_iherb(page: Page, request: IHerbRequest) -> IHerbResult:
    import urllib.parse
    url = f"https://www.iherb.com/search?kw={urllib.parse.quote_plus(request.search_query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = IHerbResult(query=request.search_query)

    checkpoint("Extract product listings")
    js_code = """(max) => {
        const results = [];
        const cards = document.querySelectorAll('.product-cell-container');
        for (const card of cards) {
            if (results.length >= max) break;
            const lines = card.innerText.split('\\n').map(l => l.trim()).filter(l => l);
            if (lines.length < 4) continue;
            // Find product name (long text, not UI labels)
            let name = '';
            let nameIdx = -1;
            for (let i = 0; i < lines.length; i++) {
                if (lines[i].length > 20 && !lines[i].match(/^(Deal|Add to|\\+|\\d+K\\+|Best Seller)/i)) {
                    name = lines[i]; nameIdx = i; break;
                }
            }
            if (!name) continue;
            if (results.some(r => r.name === name)) continue;
            // Brand = first part before comma
            let brand = '';
            const ci = name.indexOf(',');
            if (ci > 0) brand = name.substring(0, ci).trim();
            // Price = first $X.XX
            let price = '';
            for (let i = nameIdx; i < lines.length; i++) {
                const pm = lines[i].match(/\\$(\\d[\\d,.]*)/);
                if (pm) { price = '$' + pm[1]; break; }
            }
            // Rating = review count (digits with commas after name)
            let rating = '';
            if (nameIdx + 1 < lines.length) {
                const rc = lines[nameIdx + 1].replace(/,/g, '');
                if (/^\\d+$/.test(rc)) rating = lines[nameIdx + 1];
            }
            // Dosage from name
            let dosage = '';
            const dosMatch = name.match(/(\\d[\\d,]*\\s*(?:IU|mcg|mg|\\u00b5g))/i);
            if (dosMatch) dosage = dosMatch[1];
            // Servings from name
            let servings = '';
            const servMatch = name.match(/(\\d+)\\s*(?:\\w+\\s+)*(?:Count|Capsules?|Tablets?|Softgels?|Gummies|Pieces|Veggie Caps|Caplets)/i);
            if (servMatch) servings = servMatch[1];
            results.push({ name, brand, price, dosage, servings, rating });
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ProductItem()
        item.name = d.get("name", "")
        item.brand = d.get("brand", "")
        item.price = d.get("price", "")
        item.dosage = d.get("dosage", "")
        item.servings = d.get("servings", "")
        item.rating = d.get("rating", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} products for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.name}")
        print(f"     Brand: {item.brand}  Price: {item.price}")
        print(f"     Dosage: {item.dosage}  Servings: {item.servings}  Rating: {item.rating}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("iherb")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_iherb(page, IHerbRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} products")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
