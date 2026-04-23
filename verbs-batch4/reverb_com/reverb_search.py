import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class ReverbSearchRequest:
    search_term: str = "Fender Stratocaster"
    max_results: int = 5

@dataclass(frozen=True)
class ReverbListing:
    item_title: str = ""
    condition: str = ""
    price: str = ""
    url: str = ""
    image_url: str = ""

@dataclass(frozen=True)
class ReverbSearchResult:
    listings: list = None  # list[ReverbListing]

# Search Reverb.com for musical instruments matching a search term
# and extract item title, condition, price, URL, and image URL.
def reverb_search(page: Page, request: ReverbSearchRequest) -> ReverbSearchResult:
    search_term = request.search_term
    max_results = request.max_results
    print(f"  Search term: {search_term}")
    print(f"  Max results: {max_results}\n")

    search_url = (
        f"https://reverb.com/marketplace?query={search_term.replace(' ', '+')}"
        f"&skip_autodirects=true"
    )
    print(f"Loading {search_url}...")
    checkpoint("Navigate to Reverb marketplace search")
    page.goto(search_url, wait_until="domcontentloaded")

    def _wait_for_listings():
        """Wait until item links are present and the page stops navigating."""
        for attempt in range(40):
            try:
                page.wait_for_load_state("domcontentloaded", timeout=5000)
            except Exception:
                pass
            try:
                count = page.evaluate(
                    "document.querySelectorAll(\"a[href*='/item/']\").length"
                )
                if count > 0:
                    return count
            except Exception:
                pass
            page.wait_for_timeout(1000)
        return 0

    link_count = _wait_for_listings()
    print(f"  Initial links found: {link_count}")

    # Final stabilization — wait for network to settle
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(3000)
    print(f"  Loaded: {page.url}")

    # Dismiss cookie banner
    for selector in [
        'button:has-text("Accept")',
        'button:has-text("Accept All")',
        'button:has-text("Got It")',
        '#onetrust-accept-btn-handler',
    ]:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=1000):
                checkpoint(f"Dismiss cookie banner: {selector}")
                btn.click()
                page.wait_for_timeout(500)
                break
        except Exception:
            pass

    results = []

    # Extract listing data via Playwright locator API (more resilient to
    # SPA context destruction than page.evaluate or page.content).
    checkpoint("Extract listing data from search results")
    condition_re = re.compile(
        r'((?:Used|New)\s*[\u2013\u2014\u2013–-]\s*(?:Mint|Excellent|Very Good|Good|Fair|Poor)'
        r'|Brand New)',
        re.IGNORECASE,
    )
    price_re = re.compile(r'\$(\d[\d,]*(?:\.\d{2})?)')

    for _retry in range(5):
        try:
            # Wait for at least one item link to be attached
            page.locator("a[href*='/item/']").first.wait_for(state="attached", timeout=10000)

            all_links = page.locator("a[href*='/item/']").all()
            seen_titles = set()
            for a in all_links:
                if len(results) >= max_results:
                    break
                try:
                    href = a.get_attribute("href") or ""
                    if not href.startswith("/item/"):
                        continue
                    title = (a.text_content() or "").strip()
                    if len(title) < 5 or title in seen_titles:
                        continue
                    seen_titles.add(title)

                    # Get price/condition from the parent <li>
                    card_text = ""
                    try:
                        li = a.locator("xpath=ancestor::li")
                        card_text = li.text_content(timeout=2000) or ""
                    except Exception:
                        pass

                    price_match = price_re.search(card_text)
                    price = f"${price_match.group(1)}" if price_match else "N/A"

                    cond_match = condition_re.search(card_text)
                    condition = cond_match.group(1) if cond_match else "N/A"

                    clean_href = href.split("?")[0]
                    results.append(ReverbListing(
                        item_title=title,
                        condition=condition,
                        price=price,
                        url=f"https://reverb.com{clean_href}",
                        image_url="N/A",
                    ))
                except Exception:
                    continue

            print(f"  Extracted {len(results)} listings via locator API")
            if results:
                break
            # Got 0 results despite links existing — retry
            if _retry < 4:
                print(f"  Got 0 results, retrying ({_retry+1}/5)...")
                page.wait_for_timeout(3000)
        except Exception as e:
            if _retry < 4:
                print(f"  Extraction attempt {_retry+1} failed ({e}), retrying...")
                page.wait_for_timeout(3000)
                _wait_for_listings()
                page.wait_for_timeout(2000)
            else:
                print(f"  All retries failed: {e}")

    print("=" * 60)
    print(f"Reverb - Search Results for \"{search_term}\"")
    print("=" * 60)
    for idx, l in enumerate(results, 1):
        print(f"\n{idx}. {l.item_title}")
        print(f"   Condition: {l.condition}")
        print(f"   Price: {l.price}")
        print(f"   URL: {l.url}")

    print(f"\nFound {len(results)} listings")

    return ReverbSearchResult(listings=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = reverb_search(page, ReverbSearchRequest())
        print(f"\nReturned {len(result.listings or [])} listings")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
