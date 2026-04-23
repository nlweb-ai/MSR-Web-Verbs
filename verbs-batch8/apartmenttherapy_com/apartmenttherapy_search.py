"""
Auto-generated Playwright script (Python)
Apartment Therapy – Search Articles
Query: "small kitchen ideas"

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ApartmentTherapyRequest:
    search_query: str = "small kitchen ideas"
    max_results: int = 5


@dataclass
class Article:
    title: str = ""
    author: str = ""
    publish_date: str = ""
    category: str = ""
    summary: str = ""


@dataclass
class ApartmentTherapyResult:
    articles: list = field(default_factory=list)


def apartmenttherapy_search(page: Page, request: ApartmentTherapyRequest) -> ApartmentTherapyResult:
    """Search apartmenttherapy.com for articles."""
    print(f"  Query: {request.search_query}\n")

    # ── Search ────────────────────────────────────────────────────────
    search_url = f"https://www.apartmenttherapy.com/search?q={quote_plus(request.search_query)}"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to Apartment Therapy search")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Extract articles ──────────────────────────────────────────────
    raw_articles = page.evaluate(r"""(maxResults) => {
        const results = [];
        // Try multiple selector strategies
        let cards = document.querySelectorAll('article');
        if (cards.length === 0) cards = document.querySelectorAll('[data-testid*="card"], [data-testid*="result"]');
        if (cards.length === 0) cards = document.querySelectorAll('a[href*="/design/"], a[href*="/living/"], a[href*="/organize/"]');
        if (cards.length === 0) {
            // Fallback: find all links with substantial text that look like articles
            const allLinks = document.querySelectorAll('a[href]');
            const seen = new Set();
            for (const a of allLinks) {
                if (results.length >= maxResults) break;
                const href = a.getAttribute('href') || '';
                if (!href.includes('apartmenttherapy.com') && !href.startsWith('/')) continue;
                if (href.includes('/search') || href.includes('/category') || href.includes('#')) continue;
                const text = a.innerText.trim();
                if (text.length > 20 && !seen.has(text)) {
                    seen.add(text);
                    results.push({
                        title: text.split('\n')[0].trim(),
                        author: '',
                        publish_date: '',
                        category: '',
                        summary: text.split('\n').slice(1).join(' ').trim().substring(0, 200),
                    });
                }
            }
            return results;
        }
        for (let i = 0; i < Math.min(cards.length, maxResults); i++) {
            const card = cards[i];
            const titleEl = card.querySelector('h2, h3, h4') || card;
            const authorEl = card.querySelector('[class*="author"], [class*="byline"]');
            const dateEl = card.querySelector('time, [class*="date"]');
            const catEl = card.querySelector('[class*="category"], [class*="tag"]');
            const summaryEl = card.querySelector('p');

            const title = titleEl ? titleEl.innerText.trim().split('\n')[0] : '';
            if (title.length < 5) continue;

            results.push({
                title: title,
                author: authorEl ? authorEl.innerText.trim() : '',
                publish_date: dateEl ? (dateEl.getAttribute('datetime') || dateEl.innerText.trim()) : '',
                category: catEl ? catEl.innerText.trim() : '',
                summary: summaryEl ? summaryEl.innerText.trim().substring(0, 200) : '',
            });
        }
        return results;
    }""", request.max_results)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Apartment Therapy: {request.search_query}")
    print("=" * 60)
    for idx, a in enumerate(raw_articles, 1):
        print(f"\n  {idx}. {a['title']}")
        print(f"     Author: {a['author']}")
        print(f"     Date: {a['publish_date']}")
        print(f"     Category: {a['category']}")
        print(f"     Summary: {a['summary'][:100]}...")

    articles = [Article(**a) for a in raw_articles]
    return ApartmentTherapyResult(articles=articles)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("apartmenttherapy_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = apartmenttherapy_search(page, ApartmentTherapyRequest())
            print(f"\nReturned {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
