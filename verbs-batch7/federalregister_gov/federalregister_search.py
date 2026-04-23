"""
Auto-generated Playwright script (Python)
Federal Register – Search documents

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class SearchRequest:
    search_query: str = "artificial intelligence"
    max_results: int = 5


@dataclass
class Document:
    title: str = ""
    agency: str = ""
    document_type: str = ""
    publication_date: str = ""
    summary: str = ""
    url: str = ""


@dataclass
class SearchResult:
    documents: List[Document] = field(default_factory=list)


def federalregister_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search Federal Register and extract document results."""
    print(f"  Query: {request.search_query}\n")

    encoded = quote_plus(request.search_query)
    url = f"https://www.federalregister.gov/documents/search?conditions%5Bterm%5D={encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Federal Register search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = SearchResult()

    checkpoint("Extract document cards")
    docs_data = page.evaluate(
        r"""(max) => {
            const wrappers = document.querySelectorAll('.document-wrapper');
            const items = [];
            for (let i = 0; i < wrappers.length && items.length < max; i++) {
                const w = wrappers[i];
                const titleLink = w.querySelector('h5 a');
                if (!titleLink) continue;

                const title = titleLink.textContent.trim();
                const url = titleLink.href;

                // Agency and date from the text after the title
                const text = w.innerText.trim();
                const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);

                // Look for "by the <agency> on <date>" pattern
                let agency = '';
                let pubDate = '';
                for (const line of lines) {
                    const byMatch = line.match(/^by the (.+?) on (\d{2}\/\d{2}\/\d{4})/);
                    if (byMatch) {
                        agency = byMatch[1];
                        pubDate = byMatch[2];
                    }
                }

                // Document type from parent li's icon span
                const parentLi = w.closest('li.search-result-document');
                const typeIcon = parentLi ? parentLi.querySelector('span.icon-doctype') : null;
                const docType = typeIcon ? (typeIcon.getAttribute('data-tooltip') || '') : '';

                // Summary is usually the paragraph text
                const summaryLines = lines.filter(l =>
                    l !== title && !l.startsWith('by the') && l.length > 50
                );
                const summary = summaryLines[0] || '';

                items.push({title, agency, publication_date: pubDate, document_type: docType, summary, url});
            }
            return items;
        }""",
        request.max_results,
    )

    for d in docs_data:
        doc = Document()
        doc.title = d.get("title", "")
        doc.agency = d.get("agency", "")
        doc.document_type = d.get("document_type", "")
        doc.publication_date = d.get("publication_date", "")
        doc.summary = d.get("summary", "")
        doc.url = d.get("url", "")
        result.documents.append(doc)

    for i, d in enumerate(result.documents, 1):
        print(f"\n  Document {i}:")
        print(f"    Title:    {d.title}")
        print(f"    Agency:   {d.agency}")
        print(f"    Date:     {d.publication_date}")
        print(f"    Type:     {d.document_type}")
        print(f"    Summary:  {d.summary[:150]}...")
        print(f"    URL:      {d.url}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("fedreg")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = federalregister_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.documents)} documents")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
