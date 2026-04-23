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
class BritannicaSearchRequest:
    search_term: str = "photosynthesis"
    max_facts: int = 10

@dataclass(frozen=True)
class BritannicaArticle:
    title: str = ""
    summary: str = ""
    facts: list = None  # list[str]
    url: str = ""

@dataclass(frozen=True)
class BritannicaSearchResult:
    article: BritannicaArticle = None

# Search for an encyclopedia article on britannica.com, click the top result,
# and extract the article title, introductory summary paragraph, and key facts.
def britannica_search(page: Page, request: BritannicaSearchRequest) -> BritannicaSearchResult:
    search_term = request.search_term
    max_facts = request.max_facts
    print(f"  Search term: {search_term}")
    print(f"  Max facts: {max_facts}\n")

    url = f"https://www.britannica.com/search?query={quote_plus(search_term)}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to search results for '{search_term}'")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    print(f"  Loaded: {page.url}")

    # Wait for search results to appear
    try:
        page.locator('.search-results a, .results a').first.wait_for(state="attached", timeout=15000)
    except Exception:
        # Retry once if results didn't load
        print("  Results not loaded, retrying...")
        page.reload(wait_until="domcontentloaded")
        page.wait_for_timeout(8000)

    # Find the top result href and navigate directly (more reliable than clicking)
    checkpoint("Navigate to the top search result article")
    article_href = None
    for sel in ['.search-results a[href*="/science/"]', '.search-results a[href*="/topic/"]',
                '.search-results a[href*="/biography/"]', '.search-results a[href*="/place/"]',
                '.search-results a[href*="/technology/"]', '.search-results a[href*="/art/"]',
                '.results a']:
        links = page.locator(sel)
        for i in range(min(10, links.count())):
            href = links.nth(i).get_attribute("href") or ""
            if href and "/search" not in href:
                article_href = href
                break
        if article_href:
            break

    if article_href:
        if not article_href.startswith("http"):
            article_href = "https://www.britannica.com" + article_href
        page.goto(article_href, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        print(f"  Navigated to: {page.url}")
    else:
        print("  WARNING: Could not find a search result link")

    article_url = page.url

    # Extract title from h1
    title = ""
    try:
        page.locator("h1").first.wait_for(state="visible", timeout=5000)
        title = page.locator("h1").first.inner_text(timeout=3000).strip()
    except Exception:
        pass
    print(f"  Title: {title}")

    # Extract introductory summary from topic paragraphs
    summary = ""
    all_para_texts = []
    paragraphs = page.locator("p.topic-paragraph, article p")
    para_count = paragraphs.count()
    for i in range(para_count):
        try:
            txt = paragraphs.nth(i).inner_text(timeout=3000).strip()
            if txt:
                all_para_texts.append(txt)
        except Exception:
            continue
    if all_para_texts:
        summary = all_para_texts[0]

    # Extract key facts by splitting paragraphs into sentences
    facts = []
    fact_keywords = re.compile(
        r'\d+\s*%|\d{4}|\d+\s*(million|billion|thousand|km|miles|kg|lb|meters|feet)'
        r'|is\s+(?:a|an|the)|was\s+(?:a|an|the|born|discovered|founded)'
        r'|known\s+(?:as|for)|located\s+in|discovered\s+(?:by|in)', re.I
    )
    for para_text in all_para_texts:
        if len(facts) >= max_facts:
            break
        sentences = re.split(r'(?<=[.!?])\s+', para_text)
        for sent in sentences:
            if len(facts) >= max_facts:
                break
            sent = sent.strip()
            if 20 < len(sent) < 500 and fact_keywords.search(sent):
                facts.append(sent)

    # If not enough, add full paragraphs as facts
    junk_re = re.compile(r'subscribe|unsubscribe|sign up|log in|cookie|privacy', re.I)
    if len(facts) < 3:
        for para_text in all_para_texts:
            if len(facts) >= max_facts:
                break
            if para_text != summary and para_text not in facts and not junk_re.search(para_text):
                facts.append(para_text[:500])

    print("=" * 60)
    print(f"Britannica - {title}")
    print("=" * 60)

    print(f"\nSummary:\n  {summary[:300]}{'...' if len(summary) > 300 else ''}")

    print(f"\nKey Facts ({len(facts)}):")
    for idx, fact in enumerate(facts, 1):
        print(f"  {idx}. {fact[:200]}{'...' if len(fact) > 200 else ''}")

    print(f"\nURL: {article_url}")

    return BritannicaSearchResult(
        article=BritannicaArticle(
            title=title,
            summary=summary,
            facts=facts,
            url=article_url,
        )
    )

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = britannica_search(page, BritannicaSearchRequest())
        article = result.article
        print(f"\nReturned article: {article.title if article else 'None'}")
        print(f"  Facts: {len(article.facts or []) if article else 0}")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
