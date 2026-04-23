"""
FactCheck.org – Search for fact-check articles by keyword

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class FactcheckSearchRequest:
    search_query: str = "climate change"
    max_results: int = 5


@dataclass
class FactcheckArticleItem:
    title: str = ""
    author: str = ""
    publish_date: str = ""
    claim_reviewed: str = ""
    verdict: str = ""
    summary: str = ""


@dataclass
class FactcheckSearchResult:
    items: List[FactcheckArticleItem] = field(default_factory=list)


# Search for fact-check articles on FactCheck.org by keyword.
def factcheck_search(page: Page, request: FactcheckSearchRequest) -> FactcheckSearchResult:
    """Search for fact-check articles on FactCheck.org."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://www.factcheck.org/?s={query}"
    print(f"Loading {url}...")
    checkpoint("Navigate to FactCheck.org search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = FactcheckSearchResult()

    checkpoint("Extract fact-check article listings")
    js_code = r"""(max) => {
        const items = [];
        const seen = new Set();
        
        // Find links to articles
        const links = document.querySelectorAll('a[href]');
        for (const a of links) {
            if (items.length >= max) break;
            const href = a.getAttribute('href') || '';
            // FactCheck.org article URLs contain /year/month/
            if (!href.match(/factcheck\.org\/\d{4}\/\d{2}\//)) continue;
            
            const title = a.innerText.trim().split('\n')[0].trim();
            if (title.length < 10 || seen.has(title)) continue;
            seen.add(title);
            
            const card = a.closest('article, div, li') || a;
            const fullText = card.innerText.trim();
            const lines = fullText.split('\n').filter(l => l.trim());
            
            let author = '';
            let pubDate = '';
            let summary = '';
            for (const line of lines) {
                if (line.match(/^by\s+/i)) author = line.replace(/^by\s+/i, '');
                if (line.match(/\w+\s+\d{1,2},\s+\d{4}/)) pubDate = line;
                if (line.length > 30 && line !== title && !summary) summary = line.substring(0, 200);
            }
            
            items.push({title, author, publish_date: pubDate, claim_reviewed: '', verdict: '', summary});
        }
        
        // Fallback: headings
        if (items.length === 0) {
            const headings = document.querySelectorAll('h2, h3');
            for (const h of headings) {
                if (items.length >= max) break;
                const title = h.innerText.trim();
                if (title.length > 10 && !seen.has(title)) {
                    seen.add(title);
                    items.push({title, author: '', publish_date: '', claim_reviewed: '', verdict: '', summary: ''});
                }
            }
        }
        
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = FactcheckArticleItem()
        item.title = d.get("title", "")
        item.author = d.get("author", "")
        item.publish_date = d.get("publish_date", "")
        item.claim_reviewed = d.get("claim_reviewed", "")
        item.verdict = d.get("verdict", "")
        item.summary = d.get("summary", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Article {i}:")
        print(f"    Title:   {item.title}")
        print(f"    Author:  {item.author}")
        print(f"    Date:    {item.publish_date}")
        print(f"    Claim:   {item.claim_reviewed[:80]}...")
        print(f"    Verdict: {item.verdict}")
        print(f"    Summary: {item.summary[:100]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("factcheck")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = FactcheckSearchRequest()
            result = factcheck_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} fact-check articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
