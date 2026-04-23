import os
from dataclasses import dataclass
from urllib.parse import quote as url_quote
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class GuardianSearchRequest:
    search_term: str = "climate change policy"
    max_results: int = 5

@dataclass(frozen=True)
class GuardianArticle:
    headline: str = ""
    author: str = ""
    publication_date: str = ""
    summary: str = ""

@dataclass(frozen=True)
class GuardianSearchResult:
    articles: list = None  # list[GuardianArticle]

# Search The Guardian for articles matching a search term
# and extract headline, author, publication date, and summary.
def guardian_search(page: Page, request: GuardianSearchRequest) -> GuardianSearchResult:
    search_term = request.search_term
    max_results = request.max_results
    print(f"  Search term: {search_term}")
    print(f"  Max results: {max_results}\n")

    # Use Google site-restricted search for Guardian articles
    search_url = f"https://www.google.com/search?q={url_quote(search_term)}+site%3Atheguardian.com"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to Google search for Guardian articles")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    print(f"  Loaded: {page.url}")

    # Extract Guardian article URLs from Google results
    checkpoint("Extract Guardian article links from search results")
    link_els = page.locator('a[href*="theguardian.com"] h3')
    link_count = link_els.count()
    print(f"  Found {link_count} Guardian result links")

    article_urls = []
    for i in range(min(link_count, max_results)):
        try:
            h3 = link_els.nth(i)
            parent_a = h3.locator("xpath=ancestor::a[1]")
            href = parent_a.get_attribute("href", timeout=2000)
            if href and "theguardian.com" in href:
                article_urls.append(href)
        except Exception:
            continue

    print(f"  Collected {len(article_urls)} article URLs")

    results = []

    # Visit each article and extract details
    for idx, url in enumerate(article_urls):
        try:
            print(f"  Visiting article {idx + 1}: {url}")
            checkpoint(f"Visit Guardian article {idx + 1}")
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            # Dismiss cookie/consent banners
            for selector in [
                'button:has-text("Accept")',
                'button:has-text("Yes")',
                'button:has-text("OK")',
                '[data-link-name="reject all"]',
            ]:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=1000):
                        btn.click()
                        page.wait_for_timeout(500)
                        break
                except Exception:
                    pass

            # Headline
            headline = "N/A"
            try:
                h_el = page.locator('h1, [data-gu-name="headline"] h1').first
                headline = h_el.inner_text(timeout=3000).strip()
            except Exception:
                pass

            # Author
            author = "N/A"
            try:
                a_el = page.locator('[rel="author"], address a, [data-link-name="byline"]').first
                author = a_el.inner_text(timeout=2000).strip()
            except Exception:
                pass

            # Publication date
            pub_date = "N/A"
            try:
                d_el = page.locator('time[datetime], [data-gu-name="meta"] time, label[for="dateToggle"] ~ time, details time').first
                pub_date = d_el.get_attribute("datetime", timeout=2000) or d_el.inner_text(timeout=2000)
                pub_date = pub_date.strip()
            except Exception:
                try:
                    pub_date = page.evaluate("""() => {
                        const meta = document.querySelector('meta[property="article:published_time"], meta[name="DC.date.issued"]');
                        return meta ? meta.content : "N/A";
                    }""")
                except Exception:
                    pass

            # Summary / standfirst
            summary = "N/A"
            try:
                s_el = page.locator('[data-gu-name="standfirst"] p, [class*="standfirst"] p, article p').first
                summary = s_el.inner_text(timeout=2000).strip()
            except Exception:
                pass

            results.append(GuardianArticle(
                headline=headline,
                author=author,
                publication_date=pub_date,
                summary=summary[:200],
            ))
        except Exception:
            continue

    print("=" * 60)
    print(f"The Guardian - Articles for \"{search_term}\"")
    print("=" * 60)
    for idx, a in enumerate(results, 1):
        print(f"\n{idx}. {a.headline}")
        print(f"   Author: {a.author}")
        print(f"   Date: {a.publication_date}")
        print(f"   Summary: {a.summary[:100]}")

    print(f"\nFound {len(results)} articles")

    return GuardianSearchResult(articles=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = guardian_search(page, GuardianSearchRequest())
        print(f"\nReturned {len(result.articles or [])} articles")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
