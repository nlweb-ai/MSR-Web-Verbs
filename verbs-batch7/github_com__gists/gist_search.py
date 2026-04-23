"""
Auto-generated Playwright script (Python)
GitHub Gists – Search for gists

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, urllib.parse
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GistSearchRequest:
    search_query: str = "python web scraper"
    max_results: int = 5


@dataclass
class Gist:
    author: str = ""
    description: str = ""
    stars: str = "0"
    forks: str = "0"
    url: str = ""
    created: str = ""


@dataclass
class GistSearchResult:
    gists: List[Gist] = field(default_factory=list)


def gist_search(page: Page, request: GistSearchRequest) -> GistSearchResult:
    """Search GitHub Gists and extract results."""
    print(f"  Query: {request.search_query}")
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Navigate to Gist search")
    q = urllib.parse.quote_plus(request.search_query)
    page.goto(f"https://gist.github.com/search?q={q}", wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract gist results")
    result = GistSearchResult()

    items = page.evaluate(
        r"""(max) => {
            const snippets = document.querySelectorAll('.gist-snippet');
            const results = [];
            for (let i = 0; i < snippets.length && results.length < max; i++) {
                const s = snippets[i];
                
                // Stars, forks from meta list
                const metaItems = s.querySelectorAll('.gist-snippet-meta li');
                let stars = '0', forks = '0';
                for (const li of metaItems) {
                    const t = li.textContent.trim();
                    const stMatch = t.match(/(\d+)\s*star/);
                    const fkMatch = t.match(/(\d+)\s*fork/);
                    if (stMatch) stars = stMatch[1];
                    if (fkMatch) forks = fkMatch[1];
                }
                
                // Author + gist URL from links
                const allLinks = s.querySelectorAll('a');
                let author = '';
                let gistUrl = '';
                for (const a of allLinks) {
                    const href = a.getAttribute('href') || '';
                    if (href.match(/^\/[^\/]+\/[a-f0-9]{20,}/)) {
                        const parts = href.split('/').filter(Boolean);
                        if (!author && parts.length >= 2) author = parts[0];
                        if (!gistUrl) gistUrl = 'https://gist.github.com' + href;
                    }
                    if (href.match(/^\/[^\/]+$/) && !href.includes('.')) {
                        const candidate = a.textContent.trim();
                        if (!candidate.includes(' ') && candidate.length < 40 && candidate.length > 0) {
                            author = candidate;
                        }
                    }
                }
                
                // Description from article heading
                const article = s.querySelector('article');
                let desc = '';
                if (article) {
                    const heading = article.querySelector('h2, h1, h3');
                    desc = heading ? heading.textContent.trim() : article.textContent.trim().slice(0, 150);
                }
                
                // Created date
                const timeEl = s.querySelector('time-ago, relative-time');
                const created = timeEl ? timeEl.getAttribute('datetime') : '';
                
                results.push({author, description: desc, stars, forks, url: gistUrl, created});
            }
            return results;
        }""",
        request.max_results,
    )

    for item in items:
        g = Gist()
        g.author = item.get("author", "")
        g.description = item.get("description", "")
        g.stars = item.get("stars", "0")
        g.forks = item.get("forks", "0")
        g.url = item.get("url", "")
        g.created = item.get("created", "")
        result.gists.append(g)

    for i, g in enumerate(result.gists):
        print(f"  Gist {i + 1}:")
        print(f"    Author:      {g.author}")
        print(f"    Description: {g.description}")
        print(f"    Stars:       {g.stars}")
        print(f"    Forks:       {g.forks}")
        print(f"    URL:         {g.url}")
        print(f"    Created:     {g.created}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("gist")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = GistSearchRequest()
            result = gist_search(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.gists)} gists")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
