"""
Auto-generated Playwright script (Python)
Devpost – Search for hackathon projects
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class DevpostSearchRequest:
    search_query: str = "machine learning"
    max_results: int = 5


@dataclass
class DevpostProjectItem:
    project_name: str = ""
    tagline: str = ""
    num_likes: str = ""
    num_comments: str = ""
    built_with: str = ""
    hackathon_name: str = ""


@dataclass
class DevpostSearchResult:
    items: List[DevpostProjectItem] = field(default_factory=list)


# Search for hackathon projects on Devpost.
def devpost_search(page: Page, request: DevpostSearchRequest) -> DevpostSearchResult:
    """Search for hackathon projects on Devpost."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://devpost.com/software/search?query={query}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Devpost search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = DevpostSearchResult()

    checkpoint("Extract project listings")
    js_code = """(max) => {
        const cards = document.querySelectorAll('[class*="software-entry"], [class*="gallery-item"], [class*="entry"], [class*="project"], article');
        const items = [];
        for (const card of cards) {
            if (items.length >= max) break;
            const nameEl = card.querySelector('h5, h4, h3, h2, [class*="title"] a, [class*="name"] a, a[class*="link"]');
            const taglineEl = card.querySelector('p[class*="tagline"], p[class*="description"], [class*="subtitle"], p');
            const likeEl = card.querySelector('[class*="like"] span, [class*="heart"] span, [class*="count"]');
            const commentEl = card.querySelector('[class*="comment"] span');
            const builtEl = card.querySelector('[class*="built"], [class*="technologies"], [class*="tech"]');
            const hackathonEl = card.querySelector('[class*="hackathon"], [class*="challenge"], [class*="submission"]');

            const project_name = nameEl ? nameEl.textContent.trim() : '';
            const tagline = taglineEl ? taglineEl.textContent.trim() : '';
            const num_likes = likeEl ? likeEl.textContent.trim() : '';
            const num_comments = commentEl ? commentEl.textContent.trim() : '';
            const built_with = builtEl ? builtEl.textContent.trim() : '';
            const hackathon_name = hackathonEl ? hackathonEl.textContent.trim() : '';

            if (project_name) {
                items.push({project_name, tagline, num_likes, num_comments, built_with, hackathon_name});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = DevpostProjectItem()
        item.project_name = d.get("project_name", "")
        item.tagline = d.get("tagline", "")
        item.num_likes = d.get("num_likes", "")
        item.num_comments = d.get("num_comments", "")
        item.built_with = d.get("built_with", "")
        item.hackathon_name = d.get("hackathon_name", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Project {i}:")
        print(f"    Name:       {item.project_name}")
        print(f"    Tagline:    {item.tagline[:80]}...")
        print(f"    Likes:      {item.num_likes}")
        print(f"    Comments:   {item.num_comments}")
        print(f"    Built with: {item.built_with}")
        print(f"    Hackathon:  {item.hackathon_name}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("devpost")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = DevpostSearchRequest()
            result = devpost_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} projects")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
