"""
Auto-generated Playwright script (Python)
Listen Notes – Search podcasts

Uses CDP-launched Chrome to avoid bot detection.
Search → collect podcast links → visit each → extract details.
"""

import os, sys, shutil, urllib.parse
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class PodcastSearchRequest:
    query: str = "machine learning"
    max_results: int = 5


@dataclass
class Podcast:
    name: str = ""
    publisher: str = ""
    description: str = ""
    total_episodes: str = ""
    latest_episode_date: str = ""


@dataclass
class PodcastSearchResult:
    podcasts: List[Podcast] = field(default_factory=list)


def podcast_search(page: Page, request: PodcastSearchRequest) -> PodcastSearchResult:
    """Search Listen Notes for podcasts and extract details."""
    print(f"  Query: {request.query}")
    print(f"  Max results: {request.max_results}\n")

    checkpoint("Search Listen Notes for podcasts")
    q = urllib.parse.quote_plus(request.query)
    page.goto(
        f"https://www.listennotes.com/search/?q={q}&type=podcast",
        wait_until="domcontentloaded",
    )
    page.wait_for_timeout(6000)

    checkpoint("Collect podcast URLs from search suggestions")
    urls = page.evaluate(
        r"""(max) => {
            // Podcast links in the suggestion area at top
            const links = document.querySelectorAll('a[href*="/podcasts/"][title]');
            const seen = new Set();
            const results = [];
            for (const a of links) {
                if (results.length >= max) break;
                const href = a.href;
                if (seen.has(href) || !href.includes('/podcasts/')) continue;
                seen.add(href);
                results.push(href);
            }
            return results;
        }""",
        request.max_results,
    )

    result = PodcastSearchResult()

    for i, url in enumerate(urls):
        checkpoint(f"Visit podcast {i + 1}")
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        info = page.evaluate(r"""() => {
            const body = document.body.innerText;
            const lines = body.split('\n').map(l => l.trim()).filter(Boolean);

            // Name from h1 - clean up badge text
            const h1 = document.querySelector('h1');
            let name = h1 ? h1.textContent.trim() : '';
            // Remove "Claimed" / "Claim" badge text and excess whitespace
            name = name.replace(/✓/g, '').replace('Claimed', '').replace('Claim', '').replace(/\s+/g, ' ').trim();

            // Publisher - look for "By" text or publisher element
            let publisher = '';
            const byEl = document.querySelector('[class*="publisher"], [class*="author"]');
            if (byEl) {
                publisher = byEl.textContent.trim();
            } else {
                for (const line of lines) {
                    if (line.startsWith('By')) {
                        publisher = line.replace(/^By\s*/, '').trim();
                        break;
                    }
                }
            }

            // Description
            let description = '';
            const descEl = document.querySelector('meta[name="description"]');
            if (descEl) {
                description = descEl.getAttribute('content') || '';
            }

            // Total episodes - look for "X episodes" or "X eps"
            let totalEpisodes = '';
            const epMatch = body.match(/(\d+)\s*(?:episodes?|eps?)\b/i);
            if (epMatch) totalEpisodes = epMatch[1];

            // Latest episode date
            let latestDate = '';
            const dateEls = document.querySelectorAll('time, [datetime]');
            for (const el of dateEls) {
                const dt = el.getAttribute('datetime') || el.textContent.trim();
                if (dt) { latestDate = dt; break; }
            }
            // Fallback: look for date patterns
            if (!latestDate) {
                const dateMatch = body.match(/(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}/);
                if (dateMatch) latestDate = dateMatch[0];
            }

            return {name, publisher, description: description.slice(0, 200), total_episodes: totalEpisodes, latest_episode_date: latestDate};
        }""")

        p = Podcast()
        p.name = info.get("name", "")
        p.publisher = info.get("publisher", "")
        p.description = info.get("description", "")
        p.total_episodes = info.get("total_episodes", "")
        p.latest_episode_date = info.get("latest_episode_date", "")
        result.podcasts.append(p)

    for i, p in enumerate(result.podcasts):
        print(f"  Podcast {i + 1}:")
        print(f"    Name:         {p.name}")
        print(f"    Publisher:    {p.publisher}")
        print(f"    Description:  {p.description[:100]}")
        print(f"    Episodes:     {p.total_episodes}")
        print(f"    Latest:       {p.latest_episode_date}")
        print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("listennotes")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = PodcastSearchRequest()
            result = podcast_search(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.podcasts)} podcasts")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
