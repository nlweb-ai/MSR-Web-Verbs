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
class ApnewsSearchRequest:
    query: str = "space exploration"
    max_results: int = 5

@dataclass(frozen=True)
class ApnewsSearchItem:
    headline: str = ""
    publication_date: str = ""
    summary: str = ""

@dataclass(frozen=True)
class ApnewsSearchResult:
    articles: list = None  # list[ApnewsSearchItem]

# Search for news stories on apnews.com matching a query and extract article
# headlines, publication dates, and summaries or first paragraphs.
def apnews_search(page: Page, request: ApnewsSearchRequest) -> ApnewsSearchResult:
    query = request.query
    max_results = request.max_results
    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    encoded_query = quote_plus(query)
    url = f"https://apnews.com/search#?q={encoded_query}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to {url}")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""

    results = []

    # Try structured extraction via search result card elements
    cards = page.locator(
        '[class*="SearchResultsModule"] [class*="PageList"] bsp-custom-headline, '
        'div.SearchResultsModule a.Link, '
        '[data-key] .PagePromo, '
        'div[class*="PagePromo"]'
    )
    count = cards.count()
    print(f"  Found {count} article cards via selectors")

    if count > 0:
        for i in range(min(count, max_results)):
            card = cards.nth(i)
            try:
                card_text = card.inner_text(timeout=3000).strip()
                lines = [l.strip() for l in card_text.split("\n") if l.strip()]

                headline = "N/A"
                publication_date = "N/A"
                summary = "N/A"

                for line in lines:
                    # Date patterns: "January 5, 2025", "Jan. 5, 2025", "2025-01-05"
                    dm = re.search(
                        r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|'
                        r'Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|'
                        r'Nov(?:ember)?|Dec(?:ember)?)'
                        r'\.?\s+\d{1,2},?\s+\d{4}', line, re.I
                    )
                    if dm and publication_date == "N/A":
                        publication_date = dm.group(0).strip()
                        continue
                    dm2 = re.search(r'\d{4}-\d{2}-\d{2}', line)
                    if dm2 and publication_date == "N/A":
                        publication_date = dm2.group(0)
                        continue
                    # Headline: first substantial line (>10 chars, not a date)
                    if headline == "N/A" and len(line) > 10:
                        headline = line
                        continue
                    # Summary: next substantial line after headline
                    if headline != "N/A" and summary == "N/A" and len(line) > 20:
                        summary = line
                        continue

                if headline != "N/A":
                    results.append(ApnewsSearchItem(
                        headline=headline,
                        publication_date=publication_date,
                        summary=summary,
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
            # Look for lines that look like headlines (substantial text, no special chars)
            if len(line) > 15 and not re.match(r'^[\d$%]', line) and not re.match(r'^(AP News|Search|Menu|Show)', line, re.I):
                headline = line
                publication_date = "N/A"
                summary = "N/A"

                # Search nearby lines for date and summary
                for j in range(i + 1, min(len(text_lines), i + 6)):
                    nearby = text_lines[j]
                    dm = re.search(
                        r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|'
                        r'Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|'
                        r'Nov(?:ember)?|Dec(?:ember)?)'
                        r'\.?\s+\d{1,2},?\s+\d{4}', nearby, re.I
                    )
                    if dm and publication_date == "N/A":
                        publication_date = dm.group(0).strip()
                        continue
                    dm2 = re.search(r'\d{4}-\d{2}-\d{2}', nearby)
                    if dm2 and publication_date == "N/A":
                        publication_date = dm2.group(0)
                        continue
                    if summary == "N/A" and len(nearby) > 30 and nearby != headline:
                        summary = nearby

                if publication_date != "N/A" or summary != "N/A":
                    results.append(ApnewsSearchItem(
                        headline=headline,
                        publication_date=publication_date,
                        summary=summary,
                    ))
            i += 1

    print("=" * 60)
    print(f"AP News – Search Results for \"{query}\"")
    print("=" * 60)
    for idx, a in enumerate(results, 1):
        print(f"\n{idx}. {a.headline}")
        print(f"   Date: {a.publication_date}")
        print(f"   Summary: {a.summary}")

    print(f"\nFound {len(results)} articles")

    return ApnewsSearchResult(articles=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = apnews_search(page, ApnewsSearchRequest())
        print(f"\nReturned {len(result.articles or [])} articles")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
