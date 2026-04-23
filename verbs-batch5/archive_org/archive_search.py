"""
Auto-generated Playwright script (Python)
archive.org – Search & Extract
Query: history of computing

Generated on: 2026-04-17T23:58:49.563Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from playwright.sync_api import Playwright, sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ArchiveSearchRequest:
    search_query: str = "history of computing"
    collection: str = "texts"
    max_results: int = 5


@dataclass(frozen=True)
class ArchiveResult:
    title: str = ""
    creator: str = ""
    date_published: str = ""
    views: str = ""


@dataclass(frozen=True)
class ArchiveSearchResult:
    items: list = None  # list[ArchiveResult]


def archive_search(page: Page, request: ArchiveSearchRequest) -> ArchiveSearchResult:
    """Search archive.org and extract results from shadow DOM."""
    search_query = request.search_query
    collection = request.collection
    max_results = request.max_results
    print(f"  Query: {search_query}")
    print(f"  Collection: {collection}")
    print(f"  Max results: {max_results}\n")

    # ── Navigate to search results page ───────────────────────────────
    query_encoded = search_query.replace(" ", "+")
    url = f"https://archive.org/search?query={query_encoded}&and[]=mediatype%3A%22{collection}%22"
    print(f"Loading {url}...")
    checkpoint("Navigate to archive.org search page")
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(15000)
    print(f"  Loaded: {page.url}")

    # ── Extract results from shadow DOM via JS evaluation ─────────────
    checkpoint("Extract results from shadow DOM tile-dispatcher models")
    results_data = page.evaluate("""(maxResults) => {
        const appRoot = document.querySelector('app-root');
        if (!appRoot || !appRoot.shadowRoot) return [];
        const searchPage = appRoot.shadowRoot.querySelector('search-page');
        if (!searchPage || !searchPage.shadowRoot) return [];
        const collBrowser = searchPage.shadowRoot.querySelector('collection-browser');
        if (!collBrowser || !collBrowser.shadowRoot) return [];
        const scroller = collBrowser.shadowRoot.querySelector('infinite-scroller');
        if (!scroller || !scroller.shadowRoot) return [];

        const dispatchers = scroller.shadowRoot.querySelectorAll('tile-dispatcher');
        const results = [];
        for (const disp of dispatchers) {
            if (results.length >= maxResults) break;
            const model = disp.model;
            if (!model || model.hitType !== 'item') continue;
            results.push({
                title: model.title || '',
                creator: model.creator || '',
                datePublished: model.datePublished instanceof Date ? model.datePublished.toISOString() : (model.datePublished || ''),
                viewCount: model.viewCount || 0,
                identifier: model.identifier || '',
            });
        }
        return results;
    }""", max_results)

    items = []
    for r in results_data:
        date_str = r.get("datePublished", "")
        if date_str:
            date_str = str(date_str)
            # Extract just the year from ISO date
            match = re.match(r"(\d{4})", date_str)
            date_str = match.group(1) if match else date_str

        views = str(r.get("viewCount", 0))

        items.append(ArchiveResult(
            title=r.get("title", ""),
            creator=r.get("creator", "N/A") or "N/A",
            date_published=date_str or "N/A",
            views=views,
        ))

    # ── Print results ─────────────────────────────────────────────────
    print("=" * 60)
    print(f'archive.org - Search Results for "{search_query}"')
    print("=" * 60)
    for idx, item in enumerate(items, 1):
        print(f"\n{idx}. {item.title}")
        print(f"   Creator: {item.creator}")
        print(f"   Published: {item.date_published}")
        print(f"   Views: {item.views}")

    print(f"\nFound {len(items)} results")
    return ArchiveSearchResult(items=items)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("archive_org")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = archive_search(page, ArchiveSearchRequest())
            print(f"\nReturned {len(result.items or [])} items")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
