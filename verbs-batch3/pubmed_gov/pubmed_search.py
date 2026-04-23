"""
PubMed - Article Search
Search for articles on pubmed.ncbi.nlm.nih.gov and extract listings.
"""

import re
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


ARTICLE_NUM_RE = re.compile(r'^\d+$')
JOURNAL_RE = re.compile(r'^(.+?)\. (\d{4}(?:\s+\w{3,4})?)')


@dataclass(frozen=True)
class PubmedSearchRequest:
    query: str
    max_results: int = 5


@dataclass(frozen=True)
class PubmedArticle:
    title: str
    authors: str
    journal: str
    pub_date: str


@dataclass(frozen=True)
class PubmedSearchResult:
    articles: list  # list[PubmedArticle]


# Search PubMed for articles matching a query and extract title, authors, journal, and publication date for each result.
def pubmed_search(page: Page, request: PubmedSearchRequest) -> PubmedSearchResult:
    print(f"  Query: {request.query}\n")

    articles = []

    url = f"https://pubmed.ncbi.nlm.nih.gov/?term={quote_plus(request.query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Skip to 'Search Results'
    i = 0
    while i < len(text_lines):
        if text_lines[i] == 'Search Results':
            i += 1
            break
        i += 1

    while i < len(text_lines) and len(articles) < request.max_results:
        line = text_lines[i]

        # Article number
        if ARTICLE_NUM_RE.match(line) and i + 4 < len(text_lines) and text_lines[i + 1] == 'Cite':
            title = text_lines[i + 2]
            authors = text_lines[i + 3]
            journal_line = text_lines[i + 4]

            # Parse journal name and date
            jm = JOURNAL_RE.match(journal_line)
            journal = jm.group(1) if jm else journal_line
            pub_date = jm.group(2) if jm else 'N/A'

            articles.append(PubmedArticle(
                title=title,
                authors=authors,
                journal=journal,
                pub_date=pub_date,
            ))
            i += 5
            continue

        i += 1

    print("=" * 60)
    print(f"PubMed: {request.query}")
    print("=" * 60)
    for idx, r in enumerate(articles, 1):
        print(f"\n{idx}. {r.title}")
        print(f"   Authors: {r.authors}")
        print(f"   Journal: {r.journal}")
        print(f"   Date:    {r.pub_date}")

    print(f"\nFound {len(articles)} articles")

    return PubmedSearchResult(articles=articles)


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_profile = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default",
    )
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            chrome_profile,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        result = pubmed_search(page, PubmedSearchRequest(query="CRISPR gene therapy", max_results=5))
        print(f"\nReturned {len(result.articles)} articles")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)