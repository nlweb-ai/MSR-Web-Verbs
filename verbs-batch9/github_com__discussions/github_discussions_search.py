"""
Playwright script (Python) — GitHub Discussions Search
Search GitHub Discussions for topics.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class GitHubDiscussionsRequest:
    search_query: str = "machine learning best practices"
    max_results: int = 5


@dataclass
class DiscussionItem:
    title: str = ""
    repo: str = ""
    author: str = ""
    posted_time: str = ""
    answers: str = ""


@dataclass
class GitHubDiscussionsResult:
    query: str = ""
    items: List[DiscussionItem] = field(default_factory=list)


# Searches GitHub Discussions for topics matching the query and returns
# up to max_results discussions with title, repository, author, posted time, and answer count.
def search_github_discussions(page: Page, request: GitHubDiscussionsRequest) -> GitHubDiscussionsResult:
    import urllib.parse
    url = f"https://github.com/search?q={urllib.parse.quote_plus(request.search_query)}&type=discussions"
    print(f"Loading {url}...")
    checkpoint("Navigate to search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = GitHubDiscussionsResult(query=request.search_query)

    checkpoint("Extract discussion listings")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        const rl = document.querySelector('[data-testid="results-list"]');
        if (!rl) return results;
        const children = rl.children;
        for (let i = 0; i < children.length; i++) {
            if (results.length >= max) break;
            const lines = children[i].innerText.split('\\n').filter(l => l.trim());
            if (lines.length < 5) continue;
            const repo = lines[0].trim();
            const title = (lines[1].trim() === ':' ? lines[2] : lines[0]).trim();
            if (!title || seen.has(title)) continue;
            seen.add(title);
            const descIdx = lines[1].trim() === ':' ? 3 : 1;
            let author = '', posted_time = '', answers = '';
            for (let j = descIdx + 1; j < lines.length; j++) {
                const t = lines[j].trim();
                if (t === 'posted' || t === ':' || t === '\\u00b7') continue;
                if (!author && t !== 'posted') { author = t; continue; }
                if (!posted_time && (t.includes('ago') || t.startsWith('on '))) { posted_time = t; continue; }
                if (!answers && t.match(/^\\d+$/)) { answers = t; continue; }
            }
            results.push({title, repo: lines[1].trim() === ':' ? repo : '', author, posted_time, answers});
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = DiscussionItem()
        item.title = d.get("title", "")
        item.repo = d.get("repo", "")
        item.author = d.get("author", "")
        item.answers = d.get("answers", "")
        item.posted_time = d.get("posted_time", "")
        result.items.append(item)

    print(f"\nFound {len(result.items)} discussions for '{request.search_query}':")
    for i, item in enumerate(result.items, 1):
        print(f"\n  {i}. {item.title}")
        print(f"     Repo: {item.repo}  Author: {item.author}")
        print(f"     Posted: {item.posted_time}  Answers: {item.answers}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("github_disc")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = search_github_discussions(page, GitHubDiscussionsRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} discussions")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
