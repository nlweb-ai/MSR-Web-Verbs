import os
from dataclasses import dataclass
from urllib.parse import quote as url_quote
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class TechCrunchSearchRequest:
    search_term: str = "artificial intelligence startup"
    max_results: int = 5

@dataclass(frozen=True)
class TechCrunchArticle:
    headline: str = ""
    author: str = ""
    publication_date: str = ""
    summary: str = ""

@dataclass(frozen=True)
class TechCrunchSearchResult:
    articles: list = None  # list[TechCrunchArticle]

# Search TechCrunch for articles matching a search term
# and extract headline, author, publication date, and summary.
def techcrunch_search(page: Page, request: TechCrunchSearchRequest) -> TechCrunchSearchResult:
    search_term = request.search_term
    max_results = request.max_results
    print(f"  Search term: {search_term}")
    print(f"  Max results: {max_results}\n")

    search_url = f"https://techcrunch.com/?s={url_quote(search_term)}"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to TechCrunch search page")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    print(f"  Loaded: {page.url}")

    # Dismiss cookie / consent banner
    for selector in [
        '#onetrust-accept-btn-handler',
        'button:has-text("Accept All")',
        'button:has-text("Accept")',
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

    # Extract articles from search results
    checkpoint("Extract article listings from search results")
    article_cards = page.locator('div.loop-card__content')
    count = article_cards.count()
    print(f"  Found {count} loop-card__content elements")

    if count == 0:
        article_cards = page.locator('div.loop-card')
        count = article_cards.count()
        print(f"  Fallback: found {count} loop-card elements")

    seen_headlines = set()
    for i in range(count):
        if len(results) >= max_results:
            break
        card = article_cards.nth(i)
        try:
            # Headline
            headline = "N/A"
            try:
                h_el = card.locator('a.loop-card__title-link, h3.loop-card__title a').first
                headline = h_el.inner_text(timeout=2000).strip()
            except Exception:
                try:
                    h_el = card.locator('h3 a, h2 a').first
                    headline = h_el.inner_text(timeout=2000).strip()
                except Exception:
                    pass

            if headline == "N/A" or headline.lower() in seen_headlines:
                continue
            seen_headlines.add(headline.lower())

            # Author
            author = "N/A"
            try:
                a_el = card.locator('ul.loop-card__author-list a, [class*="author"] a').first
                author = a_el.inner_text(timeout=2000).strip()
            except Exception:
                pass

            # Publication date
            pub_date = "N/A"
            try:
                d_el = card.locator('time[datetime]').first
                pub_date = d_el.get_attribute("datetime", timeout=2000) or d_el.inner_text(timeout=2000)
                pub_date = pub_date.strip()
            except Exception:
                pass

            # Category
            category = "N/A"
            try:
                c_el = card.locator('span.loop-card__cat').first
                category = c_el.inner_text(timeout=1000).strip()
            except Exception:
                pass

            results.append(TechCrunchArticle(
                headline=headline,
                author=author,
                publication_date=pub_date,
                summary=f"[{category}]" if category != "N/A" else "N/A",
            ))
        except Exception:
            continue

    print("=" * 60)
    print(f"TechCrunch - Articles for \"{search_term}\"")
    print("=" * 60)
    for idx, a in enumerate(results, 1):
        print(f"\n{idx}. {a.headline}")
        print(f"   Author: {a.author}")
        print(f"   Date: {a.publication_date}")
        print(f"   Summary: {a.summary[:100]}")

    print(f"\nFound {len(results)} articles")

    return TechCrunchSearchResult(articles=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = techcrunch_search(page, TechCrunchSearchRequest())
        print(f"\nReturned {len(result.articles or [])} articles")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
