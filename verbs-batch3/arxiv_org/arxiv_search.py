"""
Playwright script (Python) — arXiv.org Search Research Papers
Query: transformer architecture
Max results: 5

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ArxivSearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class ArxivPaper:
    title: str
    authors: str
    abstract: str
    date: str


@dataclass(frozen=True)
class ArxivSearchResult:
    query: str
    papers: list[ArxivPaper]


# Searches arXiv for papers matching the given query and returns up to max_results
# papers with title, authors, abstract snippet, and submission date.
def search_arxiv_papers(
    page: Page,
    request: ArxivSearchRequest,
) -> ArxivSearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    results: list[ArxivPaper] = []

    try:
        # ── Navigate ──────────────────────────────────────────────────────
        print("Loading arXiv.org...")
        checkpoint("Navigate to https://arxiv.org")
        page.goto("https://arxiv.org")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)
        print(f"  Loaded: {page.url}")

        # ── STEP 1: Enter search query ────────────────────────────────────
        print(f'STEP 1: Search for "{query}"...')

        search_input = page.locator('input[name="query"][aria-label="Search term or terms"]').first
        checkpoint("Click search input")
        search_input.click()
        page.wait_for_timeout(500)
        page.keyboard.press("Control+a")
        checkpoint(f"Type query: {query}")
        search_input.type(query, delay=50)
        print(f'  Typed "{query}"')
        page.wait_for_timeout(1000)

        # ── STEP 2: Click Search ──────────────────────────────────────────
        print("STEP 2: Submitting search...")

        search_btn = page.locator('form[action="https://arxiv.org/search"] button[type="submit"], form.mini-search button').first
        checkpoint("Click Search button")
        search_btn.click()
        print("  Clicked Search button")

        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)
        print(f"  URL: {page.url}")

        # ── STEP 3: Extract papers ────────────────────────────────────────
        print(f"STEP 3: Extract up to {max_results} papers...")

        paper_cards = page.locator("li.arxiv-result")
        count = paper_cards.count()
        print(f"  Found {count} paper cards on page")

        for i in range(min(count, max_results)):
            card = paper_cards.nth(i)
            try:
                title = "N/A"
                try:
                    title_el = card.locator("p.title").first
                    title = title_el.inner_text(timeout=3000).strip()
                except Exception:
                    pass

                authors = "N/A"
                try:
                    authors_el = card.locator("p.authors").first
                    authors_text = authors_el.inner_text(timeout=3000).strip()
                    authors = re.sub(r"^Authors:\s*", "", authors_text).strip()
                except Exception:
                    pass

                abstract = "N/A"
                try:
                    abstract_el = card.locator("span.abstract-short").first
                    abstract_text = abstract_el.inner_text(timeout=3000).strip()
                    abstract = re.sub(r"\s*▽\s*More\s*$", "", abstract_text).strip()
                    abstract = re.sub(r"^…\s*", "", abstract).strip()
                except Exception:
                    try:
                        abstract_el = card.locator("p.abstract").first
                        abstract = abstract_el.inner_text(timeout=3000).strip()
                        abstract = re.sub(r"^Abstract:\s*", "", abstract).strip()
                        abstract = re.sub(r"\s*▽\s*More\s*$", "", abstract).strip()
                        abstract = re.sub(r"\s*△\s*Less\s*$", "", abstract).strip()
                    except Exception:
                        pass

                paper_date = "N/A"
                try:
                    date_els = card.locator("p.is-size-7")
                    for j in range(date_els.count()):
                        date_text = date_els.nth(j).inner_text(timeout=2000).strip()
                        m = re.search(r"Submitted\s+(.+?);", date_text)
                        if m:
                            paper_date = m.group(1).strip()
                            break
                except Exception:
                    pass

                if title == "N/A":
                    continue

                results.append(ArxivPaper(
                    title=title,
                    authors=authors,
                    abstract=abstract[:200] + ("..." if len(abstract) > 200 else ""),
                    date=paper_date,
                ))
            except Exception:
                continue

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nFound {len(results)} papers for '{query}':\n")
        for i, paper in enumerate(results, 1):
            print(f"  {i}. {paper.title}")
            print(f"     Authors: {paper.authors}")
            print(f"     Date: {paper.date}")
            print(f"     Abstract: {paper.abstract}")
            print()

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return ArxivSearchResult(
        query=query,
        papers=results,
    )


def test_search_arxiv_papers() -> None:
    request = ArxivSearchRequest(
        query="transformer architecture",
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
            result = search_arxiv_papers(page, request)
            assert result.query == request.query
            assert len(result.papers) <= request.max_results
            print(f"\nTotal papers found: {len(result.papers)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_arxiv_papers)
