"""
GitHub Marketplace – Search for tools and integrations by keyword

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GithubMarketplaceSearchRequest:
    search_query: str = "code review"
    max_results: int = 5


@dataclass
class GithubMarketplaceToolItem:
    tool_name: str = ""
    publisher: str = ""
    category: str = ""
    description: str = ""
    pricing: str = ""
    num_installs: str = ""
    rating: str = ""


@dataclass
class GithubMarketplaceSearchResult:
    items: List[GithubMarketplaceToolItem] = field(default_factory=list)


# Search for tools and integrations on GitHub Marketplace by keyword.
def github_marketplace_search(page: Page, request: GithubMarketplaceSearchRequest) -> GithubMarketplaceSearchResult:
    """Search for tools and integrations on GitHub Marketplace."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://github.com/marketplace?query={query}"
    print(f"Loading {url}...")
    checkpoint("Navigate to GitHub Marketplace search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = GithubMarketplaceSearchResult()

    checkpoint("Extract marketplace tool listings")
    js_code = """(max) => {
        const cards = document.querySelectorAll('[class*="marketplace"], [class*="CardBody"], [class*="card"], article, [class*="result"], a[class*="Box"]');
        const items = [];
        for (const card of cards) {
            if (items.length >= max) break;
            const nameEl = card.querySelector('h3, h2, [class*="title"], [class*="name"]');
            const publisherEl = card.querySelector('[class*="publisher"], [class*="author"], [class*="owner"], [class*="byline"]');
            const categoryEl = card.querySelector('[class*="category"], [class*="tag"], [class*="label"], [class*="type"]');
            const descEl = card.querySelector('p, [class*="description"], [class*="body"], [class*="summary"]');
            const pricingEl = card.querySelector('[class*="price"], [class*="cost"], [class*="plan"]');
            const installsEl = card.querySelector('[class*="install"], [class*="download"], [class*="usage"], [class*="count"]');
            const ratingEl = card.querySelector('[class*="rating"], [class*="star"], [class*="review"]');

            const tool_name = nameEl ? nameEl.textContent.trim() : '';
            const publisher = publisherEl ? publisherEl.textContent.trim() : '';
            const category = categoryEl ? categoryEl.textContent.trim() : '';
            const description = descEl ? descEl.textContent.trim() : '';
            const pricing = pricingEl ? pricingEl.textContent.trim() : '';
            const num_installs = installsEl ? installsEl.textContent.trim() : '';
            const rating = ratingEl ? ratingEl.textContent.trim() : '';

            if (tool_name) {
                items.push({tool_name, publisher, category, description, pricing, num_installs, rating});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = GithubMarketplaceToolItem()
        item.tool_name = d.get("tool_name", "")
        item.publisher = d.get("publisher", "")
        item.category = d.get("category", "")
        item.description = d.get("description", "")
        item.pricing = d.get("pricing", "")
        item.num_installs = d.get("num_installs", "")
        item.rating = d.get("rating", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Tool {i}:")
        print(f"    Name:        {item.tool_name}")
        print(f"    Publisher:   {item.publisher}")
        print(f"    Category:    {item.category}")
        print(f"    Description: {item.description[:80]}...")
        print(f"    Pricing:     {item.pricing}")
        print(f"    Installs:    {item.num_installs}")
        print(f"    Rating:      {item.rating}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("github_marketplace")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = GithubMarketplaceSearchRequest()
            result = github_marketplace_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} marketplace tools")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
