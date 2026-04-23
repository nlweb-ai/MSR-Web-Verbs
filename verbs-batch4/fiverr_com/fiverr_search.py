import re
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class FiverrSearchRequest:
    query: str = "logo design"
    max_results: int = 5

@dataclass(frozen=True)
class FiverrGig:
    seller_name: str = ""
    service_title: str = ""
    starting_price: str = ""
    rating: str = ""
    num_reviews: str = ""

@dataclass(frozen=True)
class FiverrSearchResult:
    gigs: list = None  # list[FiverrGig]

# Search for freelance services on fiverr.com matching a query and extract
# seller names, service titles, starting prices, ratings, and review counts.
def fiverr_search(page: Page, request: FiverrSearchRequest) -> FiverrSearchResult:
    query = request.query
    max_results = request.max_results
    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    encoded_query = quote_plus(query)
    url = f"https://www.fiverr.com/search/gigs?query={encoded_query}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to Fiverr search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""

    results = []

    # Try structured extraction via gig card elements
    cards = page.locator(
        '[class*="gig-card-layout"], '
        '[class*="GigCard"], '
        '[class*="gig-wrapper"], '
        'div[class*="BasicGigCard"], '
        'div[class*="listing-card"]'
    )
    count = cards.count()
    print(f"  Found {count} gig cards via selectors")

    if count > 0:
        for i in range(min(count, max_results)):
            card = cards.nth(i)
            try:
                card_text = card.inner_text(timeout=3000).strip()
                lines = [l.strip() for l in card_text.split("\n") if l.strip()]

                seller_name = "N/A"
                service_title = "N/A"
                starting_price = "N/A"
                rating = "N/A"
                num_reviews = "N/A"

                for line in lines:
                    # Price patterns: "From $5", "$10", "Starting at $25"
                    pm = re.search(r'(?:From\s+|Starting\s+at\s+)?\$[\d,]+(?:\.\d{2})?', line, re.I)
                    if pm and starting_price == "N/A":
                        starting_price = pm.group(0).strip()
                        continue
                    # Rating pattern: "4.9" or "5.0 (123)"
                    rm = re.search(r'\b(\d\.\d)\b', line)
                    if rm and rating == "N/A" and float(rm.group(1)) <= 5.0:
                        rating = rm.group(1)
                        # Check for review count in same line
                        rvm = re.search(r'\((\d[\d,]*k?)\)', line, re.I)
                        if rvm and num_reviews == "N/A":
                            num_reviews = rvm.group(1)
                        continue
                    # Review count standalone: "(123)", "(1k+)"
                    rvm2 = re.search(r'\((\d[\d,]*k?\+?)\)', line, re.I)
                    if rvm2 and num_reviews == "N/A":
                        num_reviews = rvm2.group(1)
                        continue
                    # Seller name: short text, often single name or "username"
                    if seller_name == "N/A" and 2 < len(line) < 40 and not re.search(r'[\$]', line):
                        seller_name = line
                        continue
                    # Service title: longer descriptive text
                    if service_title == "N/A" and len(line) > 15:
                        service_title = line
                        continue

                if service_title != "N/A" or seller_name != "N/A":
                    results.append(FiverrGig(
                        seller_name=seller_name,
                        service_title=service_title,
                        starting_price=starting_price,
                        rating=rating,
                        num_reviews=num_reviews,
                    ))
            except Exception:
                continue

    # Fallback: text-based extraction from page body
    if not results:
        print("  Card selectors missed, trying text-based extraction...")
        text_lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        i = 0
        while i < len(text_lines) and len(results) < max_results:
            line = text_lines[i]
            # Look for price indicators as anchors for gig blocks
            pm = re.search(r'(?:From\s+|Starting\s+at\s+)?\$[\d,]+(?:\.\d{2})?', line, re.I)
            if pm:
                starting_price = pm.group(0).strip()
                seller_name = "N/A"
                service_title = "N/A"
                rating = "N/A"
                num_reviews = "N/A"

                # Search nearby lines for other fields
                for j in range(max(0, i - 5), min(len(text_lines), i + 5)):
                    if j == i:
                        continue
                    nearby = text_lines[j]
                    rm = re.search(r'\b(\d\.\d)\b', nearby)
                    if rm and rating == "N/A" and float(rm.group(1)) <= 5.0:
                        rating = rm.group(1)
                        rvm = re.search(r'\((\d[\d,]*k?\+?)\)', nearby, re.I)
                        if rvm and num_reviews == "N/A":
                            num_reviews = rvm.group(1)
                        continue
                    if service_title == "N/A" and len(nearby) > 20 and not re.search(r'[\$]', nearby):
                        service_title = nearby
                        continue
                    if seller_name == "N/A" and 2 < len(nearby) < 35 and not re.search(r'[\$]', nearby) and nearby != service_title:
                        seller_name = nearby
                        continue

                if service_title != "N/A":
                    results.append(FiverrGig(
                        seller_name=seller_name,
                        service_title=service_title,
                        starting_price=starting_price,
                        rating=rating,
                        num_reviews=num_reviews,
                    ))
            i += 1

    print("=" * 60)
    print(f"Fiverr – Search Results for \"{query}\"")
    print("=" * 60)
    for idx, g in enumerate(results, 1):
        print(f"\n{idx}. {g.service_title}")
        print(f"   Seller: {g.seller_name}")
        print(f"   Price: {g.starting_price}")
        print(f"   Rating: {g.rating} ({g.num_reviews} reviews)")

    print(f"\nFound {len(results)} gigs")

    return FiverrSearchResult(gigs=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = fiverr_search(page, FiverrSearchRequest())
        print(f"\nReturned {len(result.gigs or [])} gigs")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
