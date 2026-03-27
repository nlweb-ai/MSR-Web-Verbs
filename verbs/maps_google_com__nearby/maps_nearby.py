"""
Google Maps – Nearby Search
Search: "dealerships" near "urbana champaign"

Generated on: 2026-03-19T03:13:08.694Z
Recorded 10 browser interactions
Pure Playwright – no AI.
"""

import os
import sys
from dataclasses import dataclass
from typing import List
from playwright.sync_api import Page, sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class NearbySearchRequest:
    query: str
    location: str
    max_results: int = 5


@dataclass(frozen=True)
class BusinessDetail:
    name: str
    address: str
    rating: str
    phone: str
    website: str


@dataclass(frozen=True)
class NearbySearchResult:
    query: str
    location: str
    businesses: List[BusinessDetail]


# Search Google Maps for nearby businesses, click into each result card,
# and extract name, address, review score, phone, and website URL.
def search_nearby(page: Page, request: NearbySearchRequest) -> NearbySearchResult:
    businesses = []
    seen_businesses = set()

    try:
        search_text = f"{request.query} near {request.location}"
        print(f"Loading Google Maps with query: {search_text} ...")
        encoded = search_text.replace(" ", "+")
        checkpoint("goto Google Maps nearby search")
        page.goto(f"https://www.google.com/maps/search/{encoded}/", wait_until="domcontentloaded", timeout=30000)

        # Wait for either the results feed OR a direct place page (address button)
        # Use whichever appears first to avoid long timeouts for single-business queries.
        feed_locator = page.locator("[role='feed']")
        place_locator = page.locator("button[data-item-id='address']")
        has_feed = False
        try:
            page.wait_for_selector(
                "[role='feed'], button[data-item-id='address']",
                timeout=8000,
            )
            has_feed = feed_locator.first.is_visible(timeout=200)
        except Exception:
            pass
        print(f"  Loaded: {page.url}")

        # Quick consent popup check (200ms timeout each – fast fail)
        for sel in ["button:has-text('Accept all')", "button:has-text('Reject all')",
                     "button:has-text('I agree')"]:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=200):
                    checkpoint("click consent popup button")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(300)
            except Exception:
                pass

        # Scroll the feed to load more cards (only if a feed is present)
        if has_feed:
            try:
                feed = feed_locator.first
                for _ in range(3):
                    feed.evaluate("el => el.scrollTop = el.scrollHeight")
                    page.wait_for_timeout(1000)
            except Exception:
                pass

        # Click each card in the sidebar list, extract, then click the next card directly
        # Skip sponsored cards entirely
        cards = page.locator("[role='feed'] a[href*='/maps/place/']").all()
        seen_hrefs = set()
        unique_indices = []
        for idx, c in enumerate(cards):
            # Skip sponsored cards — check the link's own text and its direct container
            try:
                is_sponsored = c.evaluate("""el => {
                    // Check the <a> element's own text
                    const ownText = el.innerText || '';
                    if (/^Sponsored$/im.test(ownText)) return true;
                    // Check immediate parent (the card wrapper div)
                    const parent = el.parentElement;
                    if (parent) {
                        // Look for a "Sponsored" span/div as a direct child or grandchild
                        const spans = parent.querySelectorAll('span, div');
                        for (const s of spans) {
                            if (s.textContent.trim() === 'Sponsored') return true;
                        }
                    }
                    return false;
                }""")
                if is_sponsored:
                    continue
            except Exception:
                pass
            href = c.get_attribute("href") or ""
            base_href = href.split("?")[0] if href else ""
            if base_href and base_href not in seen_hrefs:
                seen_hrefs.add(base_href)
                unique_indices.append(idx)
        print(f"  Found {len(unique_indices)} result cards (excluding sponsored)")

        # Fallback: if Google Maps jumped directly to a place page (no sidebar cards)
        if not unique_indices:
            print("  No result cards found — trying direct place-page extraction...")
            try:
                page.locator("button[data-item-id='address']").first.wait_for(state='attached', timeout=4000)
            except Exception:
                page.wait_for_timeout(1500)

            detail = page.evaluate(r"""() => {
                const result = {name: 'N/A', address: 'N/A', rating: 'N/A', phone: 'N/A', website: 'N/A'};

                const headings = document.querySelectorAll('h1');
                for (const h of headings) {
                    const t = h.innerText.trim();
                    if (t && t !== 'Results' && t.length > 1
                        && !/^sponsored/i.test(t)) {
                        result.name = t;
                        break;
                    }
                }
                if (result.name === 'N/A') {
                    const h2s = document.querySelectorAll('h2');
                    for (const h of h2s) {
                        const t = h.innerText.trim();
                        if (t && t !== 'Results' && !/^sponsored/i.test(t) && t.length > 1) {
                            result.name = t;
                            break;
                        }
                    }
                }

                const stars = document.querySelectorAll("[role='img'][aria-label*='star']");
                for (const s of stars) {
                    const label = s.getAttribute('aria-label') || '';
                    const m = label.match(/([\d.]+)/);
                    if (m) { result.rating = m[1]; break; }
                }

                const addrEl = document.querySelector("button[data-item-id='address']");
                if (addrEl) {
                    const lines = addrEl.innerText.split('\\n').map(l => l.trim()).filter(Boolean);
                    if (lines.length) result.address = lines[lines.length - 1];
                }

                const phoneEl = document.querySelector("button[data-item-id*='phone']");
                if (phoneEl) {
                    const t = phoneEl.innerText.trim();
                    const m = t.match(/[\(\d][\d\s\-\(\)\+]{6,}/);
                    if (m) result.phone = m[0].trim();
                }

                const siteEl = document.querySelector("a[data-item-id='authority']");
                if (siteEl) {
                    const href = siteEl.getAttribute('href') || '';
                    if (href && !href.includes('google.com')) result.website = href;
                    else { const t = siteEl.innerText.trim(); if (t && t.includes('.')) result.website = t; }
                }

                return result;
            }""")

            if detail['name'] != 'N/A':
                print(f"    Name:    {detail['name']}")
                print(f"    Address: {detail['address']}")
                print(f"    Rating:  {detail['rating']}")
                print(f"    Phone:   {detail['phone']}")
                print(f"    Website: {detail['website']}")
                businesses.append(BusinessDetail(
                    name=detail["name"],
                    address=detail["address"],
                    rating=detail["rating"],
                    phone=detail["phone"],
                    website=detail["website"],
                ))
            else:
                print("  Could not extract business details from the page.")

        for count, card_idx in enumerate(unique_indices[:request.max_results + 5]):
            # Re-query cards (indices stay the same, but DOM refs may go stale)
            cards = page.locator("[role='feed'] a[href*='/maps/place/']").all()
            if card_idx >= len(cards):
                break

            checkpoint("click result card")
            cards[card_idx].evaluate("el => el.click()")
            try:
                page.locator("button[data-item-id='address']").first.wait_for(state='attached', timeout=3000)
            except Exception:
                page.wait_for_timeout(500)

            # Extract details
            detail = page.evaluate(r"""() => {
                const result = {name: 'N/A', address: 'N/A', rating: 'N/A', phone: 'N/A', website: 'N/A'};

                const headings = document.querySelectorAll('h1');
                for (const h of headings) {
                    const t = h.innerText.trim();
                    if (t && t !== 'Results' && t.length > 1
                        && !/^sponsored/i.test(t)) {
                        result.name = t;
                        break;
                    }
                }
                // Fallback: try h2 if h1 only had Sponsored/Results
                if (result.name === 'N/A') {
                    const h2s = document.querySelectorAll('h2');
                    for (const h of h2s) {
                        const t = h.innerText.trim();
                        if (t && t !== 'Results' && !/^sponsored/i.test(t) && t.length > 1) {
                            result.name = t;
                            break;
                        }
                    }
                }

                const stars = document.querySelectorAll("[role='img'][aria-label*='star']");
                for (const s of stars) {
                    const label = s.getAttribute('aria-label') || '';
                    const m = label.match(/([\d.]+)/);
                    if (m) { result.rating = m[1]; break; }
                }

                const addrEl = document.querySelector("button[data-item-id='address']");
                if (addrEl) {
                    const lines = addrEl.innerText.split('\n').map(l => l.trim()).filter(Boolean);
                    if (lines.length) result.address = lines[lines.length - 1];
                }

                const phoneEl = document.querySelector("button[data-item-id*='phone']");
                if (phoneEl) {
                    const t = phoneEl.innerText.trim();
                    const m = t.match(/[\(\d][\d\s\-\(\)\+]{6,}/);
                    if (m) result.phone = m[0].trim();
                }

                const siteEl = document.querySelector("a[data-item-id='authority']");
                if (siteEl) {
                    const href = siteEl.getAttribute('href') || '';
                    if (href && !href.includes('google.com')) result.website = href;
                    else { const t = siteEl.innerText.trim(); if (t && t.includes('.')) result.website = t; }
                }

                return result;
            }""")

            # Dedup by name+address
            dedup_key = (detail['name'].lower().strip(), detail['address'].lower().strip())
            if dedup_key in seen_businesses:
                continue
            seen_businesses.add(dedup_key)

            print(f"    Name:    {detail['name']}")
            print(f"    Address: {detail['address']}")
            print(f"    Rating:  {detail['rating']}")
            print(f"    Phone:   {detail['phone']}")
            print(f"    Website: {detail['website']}")

            businesses.append(BusinessDetail(
                name=detail["name"],
                address=detail["address"],
                rating=detail["rating"],
                phone=detail["phone"],
                website=detail["website"],
            ))

            if len(businesses) >= request.max_results:
                break

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return NearbySearchResult(
        query=request.query,
        location=request.location,
        businesses=businesses,
    )


def test_search_nearby() -> None:
    request = NearbySearchRequest(
        query="dealerships",
        location="urbana champaign",
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
            result = search_nearby(page, request)
            print(f"\n{'='*60}")
            print(f"  Results: {len(result.businesses)} businesses")
            print(f"  Query: {result.query} near {result.location}")
            print(f"{'='*60}")
            for i, b in enumerate(result.businesses, 1):
                print(f"  {i}. {b.name}")
                print(f"     {b.address} | Rating: {b.rating} | {b.phone} | {b.website}")
        finally:
            context.close()


def test_papa_dels() -> None:
    """Test: specific single-business query that may skip the sidebar feed."""
    request = NearbySearchRequest(
        query="papa del's pizza",
        location="champaign il",
        max_results=1,
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
            result = search_nearby(page, request)
            print(f"\n{'='*60}")
            print(f"  Results: {len(result.businesses)} businesses")
            print(f"  Query: {result.query} near {result.location}")
            print(f"{'='*60}")
            for i, b in enumerate(result.businesses, 1):
                print(f"  {i}. {b.name}")
                print(f"     {b.address} | Rating: {b.rating} | {b.phone} | {b.website}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    #run_with_debugger(test_search_nearby)
    run_with_debugger(test_papa_dels)
