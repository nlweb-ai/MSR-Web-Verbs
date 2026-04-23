"""
Auto-generated Playwright script (Python)
Architectural Digest – Search Articles
Query: "home tour"

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
class ArchitecturalDigestRequest:
    search_query: str = "home tour"
    max_results: int = 5


@dataclass
class Article:
    title: str = ""
    author: str = ""
    publish_date: str = ""
    location: str = ""
    summary: str = ""


@dataclass
class ArchitecturalDigestResult:
    articles: list = field(default_factory=list)


def architecturaldigest_search(page: Page, request: ArchitecturalDigestRequest) -> ArchitecturalDigestResult:
    """Search architecturaldigest.com for home tour articles."""
    print(f"  Query: {request.search_query}\n")

    # ── Search ────────────────────────────────────────────────────────
    search_url = f"https://www.architecturaldigest.com/search?q={quote_plus(request.search_query)}"
    print(f"Loading {search_url}...")
    checkpoint("Navigate to Architectural Digest search")
    page.goto(search_url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    # ── Extract articles ──────────────────────────────────────────────
    raw_articles = page.evaluate(r"""(maxResults) => {
        const results = [];
        const seenTitles = new Set();

        // Find all h2/h3 elements that look like article titles
        const headings = document.querySelectorAll('h2, h3');
        for (const h of headings) {
            if (results.length >= maxResults) break;
            const title = h.innerText.trim();
            if (title.length < 15 || seenTitles.has(title)) continue;
            seenTitles.add(title);

            // Walk up to find the card container
            let card = h.closest('li') || h.closest('div');
            if (!card) card = h.parentElement;
            const fullText = card ? card.innerText.trim() : '';
            const lines = fullText.split('\n').filter(l => l.trim().length > 0);

            let author = '';
            let summary = '';
            for (const line of lines) {
                if (line.match(/^by\s+/i)) {
                    author = line.replace(/^by\s+/i, '').trim();
                }
                if (line.length > 30 && line !== title && !line.match(/^by\s+/i)) {
                    summary = line.substring(0, 200);
                }
            }

            const locationMatch = title.match(/in\s+([A-Z][\w\s,]+)$/);
            results.push({
                title: title,
                author: author,
                publish_date: '',
                location: locationMatch ? locationMatch[1].trim() : '',
                summary: summary,
            });
        }
        return results;
    }""", request.max_results)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Architectural Digest: {request.search_query}")
    print("=" * 60)
    for idx, a in enumerate(raw_articles, 1):
        print(f"\n  {idx}. {a['title']}")
        print(f"     Author: {a['author']}")
        print(f"     Date: {a['publish_date']}")
        if a['location']:
            print(f"     Location: {a['location']}")
        print(f"     Summary: {a['summary'][:100]}...")

    articles = [Article(**a) for a in raw_articles]
    return ArchitecturalDigestResult(articles=articles)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("architecturaldigest_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = architecturaldigest_search(page, ArchitecturalDigestRequest())
            print(f"\nReturned {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
