"""
arXiv – Recent Papers by Category (typed verb)

Uses Playwright via CDP connection with the user's Chrome profile.
"""

import os, sys, shutil, re
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

@dataclass(frozen=True)
class ArxivPapersRequest:
    category: str = "cs.CR"
    max_results: int = 5

@dataclass(frozen=True)
class ArxivPaper:
    arxiv_id: str
    title: str
    authors: list[str]
    pdf_url: str
    abstract: str

@dataclass(frozen=True)
class ArxivPapersResult:
    category: str
    papers: list[ArxivPaper]

# Retrieves the latest N papers from an arXiv subject-category listing page.
# For each paper, extracts the title, authors, abstract, arXiv ID, and PDF URL.
def search_arxiv_papers(
    page: Page,
    request: ArxivPapersRequest,
) -> ArxivPapersResult:
    category = request.category
    max_results = request.max_results
    print(f"  Category:    {category}")
    print(f"  Max results: {max_results}\n")

    listing_url = f"https://arxiv.org/list/{category}/recent"
    print(f"Loading listing: {listing_url}")
    page.goto(listing_url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_selector("dl#articles > dt", timeout=10000)
    page.wait_for_timeout(2000)

    dts = page.locator("dl#articles > dt")
    dds = page.locator("dl#articles > dd")
    total = min(dts.count(), dds.count(), max_results)
    print(f"  Found {dts.count()} entries on page; extracting top {total}.")

    # Scratch list for the two-pass extraction
    scratch: list[dict] = []

    # Pass 1: from the listing page → arxiv_id, title, authors, pdf_url
    for i in range(total):
        dt = dts.nth(i)
        dd = dds.nth(i)

        id_anchor = dt.locator('a[href^="/abs/"]').first
        href = id_anchor.get_attribute("href") or ""
        arxiv_id = href.split("/abs/")[-1] if "/abs/" in href else ""

        title_raw = dd.locator(".list-title").first.inner_text(timeout=2000)
        title = re.sub(r"^\s*Title:\s*", "", title_raw).strip()

        author_links = dd.locator(".list-authors a")
        authors = [
            author_links.nth(k).inner_text(timeout=2000).strip()
            for k in range(author_links.count())
        ]

        pdf_anchor = dt.locator('a[href^="/pdf/"]').first
        pdf_href = pdf_anchor.get_attribute("href") if pdf_anchor.count() > 0 else ""
        if pdf_href and not pdf_href.startswith("http"):
            pdf_url = f"https://arxiv.org{pdf_href}"
        elif arxiv_id:
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
        else:
            pdf_url = ""

        scratch.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": authors,
            "pdf_url": pdf_url,
            "abstract": "",
        })

    # Pass 2: visit each /abs/<id> page to grab the abstract
    for item in scratch:
        if not item["arxiv_id"]:
            continue
        abs_url = f"https://arxiv.org/abs/{item['arxiv_id']}"
        page.goto(abs_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_selector("blockquote.abstract", timeout=10000)
        page.wait_for_timeout(1500)
        abs_raw = page.locator("blockquote.abstract").first.inner_text(timeout=5000)
        item["abstract"] = re.sub(r"^\s*Abstract:\s*", "", abs_raw).strip()

    papers: list[ArxivPaper] = [
        ArxivPaper(
            arxiv_id=item["arxiv_id"],
            title=item["title"],
            authors=item["authors"],
            pdf_url=item["pdf_url"],
            abstract=item["abstract"],
        )
        for item in scratch
    ]

    # Print summary
    print(f"\nTop {len(papers)} latest papers in {category}:")
    for idx, p in enumerate(papers, 1):
        authors_preview = ", ".join(p.authors[:3])
        if len(p.authors) > 3:
            authors_preview += f", … (+{len(p.authors) - 3} more)"
        abstract_snippet = (
            (p.abstract[:200] + "…") if len(p.abstract) > 200 else p.abstract
        )
        print(f"\n  [{idx}] {p.title}")
        print(f"      arXiv ID:  {p.arxiv_id}")
        print(f"      Authors:   {authors_preview}")
        print(f"      PDF:       {p.pdf_url}")
        print(f"      Abstract:  {abstract_snippet}")

    return ArxivPapersResult(category=category, papers=papers)

def test_search_arxiv_papers() -> None:
    """Concrete test: fetch top 5 latest cs.CR papers."""
    request = ArxivPapersRequest(category="cs.CR", max_results=5)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        try:
            page = browser.new_page()
            result = search_arxiv_papers(page, request)

            assert isinstance(result, ArxivPapersResult)
            assert result.category == request.category
            assert len(result.papers) == request.max_results
            for p in result.papers:
                assert isinstance(p, ArxivPaper)
                assert p.arxiv_id and p.title
                assert p.authors and isinstance(p.authors, list)
                assert p.pdf_url.startswith("https://arxiv.org/pdf/")
                assert p.abstract

            print("\n--- Test passed ---")
            print(f"  Retrieved {len(result.papers)} typed ArxivPaper objects.")
        finally:
            try:
                browser.close()
            except Exception:
                pass

if __name__ == "__main__":
    test_search_arxiv_papers()
