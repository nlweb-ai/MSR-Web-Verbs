"""
Auto-generated Playwright script (Python)
HomeAdvisor – Service Professional Search
Service: "plumbing"
Location: "Denver, CO"

Generated on: 2026-04-18T05:34:44.102Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ServiceRequest:
    service: str = "plumbing"
    location: str = "Denver, CO"
    max_results: int = 5


@dataclass
class Professional:
    name: str = ""
    rating: str = ""
    reviews: str = ""
    years_in_business: str = ""
    phone: str = ""


@dataclass
class ServiceResult:
    professionals: List[Professional] = field(default_factory=list)


def homeadvisor_search(page: Page, request: ServiceRequest) -> ServiceResult:
    """Search HomeAdvisor for service professionals."""
    print(f"  Service: {request.service}")
    print(f"  Location: {request.location}\n")

    # HomeAdvisor is a lead-gen site; use Google to find rated pros
    from urllib.parse import quote_plus
    url = f"https://www.google.com/search?q=site:homeadvisor.com+{quote_plus(request.service)}+{quote_plus(request.location)}+rated"
    print(f"Loading {url}...")
    checkpoint("Navigate to Google for HomeAdvisor pros")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # Scroll to load content
    for _ in range(3):
        page.evaluate("window.scrollBy(0, 600)")
        page.wait_for_timeout(800)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    checkpoint("Extract professional listings")
    pros_data = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seen = new Set();

        // Extract from Google search results linking to homeadvisor.com
        const links = document.querySelectorAll('a[href*="homeadvisor.com"]');
        for (const a of links) {
            if (results.length >= maxResults) break;
            const href = a.getAttribute('href') || '';
            // Look for pro profile or rated pages
            if (!/(\/rated\.|\/sp\/)/.test(href)) continue;

            const block = a.closest('div, li') || a;
            let name = '';
            const h3 = block.querySelector('h3');
            if (h3) name = h3.innerText.trim();
            if (!name) name = a.innerText.trim();
            name = name.split('\n')[0].trim();
            // Clean up suffixes
            name = name.replace(/\s*[-|]\s*HomeAdvisor\s*$/i, '').trim();
            if (!name || name.length < 10 || seen.has(name)) continue;
            if (/^(join|sign|log|menu|home|about|read more)/i.test(name)) continue;
            seen.add(name);

            const text = block.innerText || '';
            let rating = '', reviews = '', years = '', phone = '';
            const rm = text.match(/(\d+\.?\d*)\s*(?:star|rating|\/\s*5)/i);
            if (rm) rating = rm[1];
            const revm = text.match(/(\d+)\s*(?:review|rating)/i);
            if (revm) reviews = revm[1];

            results.push({ name: name.slice(0, 80), rating, reviews, years_in_business: years, phone });
        }
        return results;
    }""", request.max_results)

    result = ServiceResult(professionals=[Professional(**p) for p in pros_data])

    print("\n" + "=" * 60)
    print(f"HomeAdvisor: {request.service} in {request.location}")
    print("=" * 60)
    for i, p in enumerate(result.professionals, 1):
        print(f"  {i}. {p.name}")
        if p.rating:
            print(f"     Rating: {p.rating}")
        if p.reviews:
            print(f"     Reviews: {p.reviews}")
        if p.years_in_business:
            print(f"     Experience: {p.years_in_business}")
        if p.phone:
            print(f"     Phone: {p.phone}")
    print(f"\nTotal: {len(result.professionals)} professionals")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("homeadvisor_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = homeadvisor_search(page, ServiceRequest())
            print(f"\nReturned {len(result.professionals)} professionals")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
