"""
PBS – Show/Video Search

Search PBS for shows/videos and extract the top results:
show name, episode title, description, and URL.
"""

import os, sys, shutil
from urllib.parse import quote
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws


@dataclass(frozen=True)
class Request:
    Query: str = "nature documentary"
    num_results: int = 5


@dataclass
class VideoResult:
    show_name: str = ""
    episode_title: str = ""
    description: str = ""
    url: str = ""


@dataclass
class Result:
    results: List[VideoResult] = field(default_factory=list)


def show_search(page, request: Request) -> Result:
    """Search PBS and extract top video results."""

    url = f"https://www.pbs.org/search/?q={quote(request.Query)}"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    data = page.evaluate(r"""(numResults) => {
        const container = document.querySelector('[class*="search_video_and_web_results"]');
        if (!container) return [];

        const allLinks = Array.from(container.querySelectorAll('a[href]'));
        const cards = [];
        const seen = new Set();

        for (const a of allLinks) {
            const href = a.href;
            if (href.includes('/video/') && !seen.has(href)) {
                seen.add(href);
                const parent = a.parentElement?.parentElement?.parentElement;
                if (!parent) continue;

                const showLink = parent.querySelector('a[href*="/show/"]');
                const titleLinks = parent.querySelectorAll('a[href*="/video/"]');
                let title = '';
                for (const tl of titleLinks) {
                    if (tl.textContent.trim()) {
                        title = tl.textContent.trim();
                        break;
                    }
                }

                // Description is in the remaining text content after the title
                const fullText = parent.textContent.trim();
                const showName = showLink?.textContent.trim() || '';
                // Extract description: everything after the title, before "Sign in"
                let desc = '';
                const idx = fullText.indexOf(title);
                if (idx >= 0) {
                    desc = fullText.slice(idx + title.length).trim();
                    const signIdx = desc.indexOf('Sign in');
                    if (signIdx >= 0) desc = desc.slice(0, signIdx).trim();
                    // Remove "Video has Closed CaptionsCC" prefix
                    desc = desc.replace(/^Video has Closed CaptionsCC\s*/, '');
                }

                cards.push({
                    showName,
                    episodeTitle: title,
                    description: desc,
                    url: href,
                });
                if (cards.length >= numResults) break;
            }
        }
        return cards;
    }""", request.num_results)

    return Result(
        results=[
            VideoResult(
                show_name=r.get("showName", ""),
                episode_title=r.get("episodeTitle", ""),
                description=r.get("description", ""),
                url=r.get("url", ""),
            )
            for r in data
        ]
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("pbs_search")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            req = Request(Query="nature documentary", num_results=5)
            result = show_search(page, req)
            print(f"\nSearch Results ({len(result.results)}):")
            for i, r in enumerate(result.results, 1):
                print(f"\n  {i}. [{r.show_name}] {r.episode_title}")
                print(f"     {r.description}")
                print(f"     {r.url}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
