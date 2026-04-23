"""
Playwright script (Python) — Mastodon Trending Posts
Browse Mastodon's explore page and extract trending posts.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MastodonRequest:
    max_results: int = 5


@dataclass
class PostItem:
    author: str = ""
    content: str = ""
    boosts: str = ""
    favorites: str = ""


@dataclass
class MastodonResult:
    posts: List[PostItem] = field(default_factory=list)


# Browses Mastodon trending posts and extracts author,
# content, boost count, and favorite count.
def browse_mastodon_trending(page: Page, request: MastodonRequest) -> MastodonResult:
    url = "https://mastodon.social/explore"
    print(f"Loading {url}...")
    checkpoint("Navigate to Mastodon explore")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    result = MastodonResult()

    checkpoint("Extract trending posts")
    js_code = """(max) => {
        const results = [];
        const seen = new Set();
        // First try proper article elements with display-name
        const articles = document.querySelectorAll('article');
        for (const art of articles) {
            if (results.length >= max) break;
            const nameEl = art.querySelector('a[class*="display-name"], .display-name, [class*="account"]');
            if (!nameEl) continue;
            const author = nameEl.textContent.trim().replace(/\\s+/g, ' ');
            if (!author) continue;
            const contentEl = art.querySelector('[class*="content"], .status__content, p');
            const content = contentEl ? contentEl.textContent.trim().substring(0, 200) : '';
            const key = author + '|' + content.substring(0, 80);
            if (seen.has(key)) continue;
            seen.add(key);
            let boosts = '0', favorites = '0';
            const buttons = art.querySelectorAll('button, [class*="icon-button"]');
            for (const btn of buttons) {
                const ariaLabel = btn.getAttribute('aria-label') || '';
                const text = btn.textContent.trim();
                if (/boost|reblog/i.test(ariaLabel)) boosts = text.replace(/[^0-9]/g, '') || '0';
                else if (/fav|like/i.test(ariaLabel)) favorites = text.replace(/[^0-9]/g, '') || '0';
            }
            results.push({ author, content, boosts, favorites });
        }
        // If not enough from DOM, parse remaining from body text (logged-out view)
        if (results.length < max) {
            const body = document.body.innerText;
            const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            for (let i = 0; i < lines.length && results.length < max; i++) {
                // Look for lines containing <p> tags (raw HTML in text = post summaries)
                if (lines[i].includes('<p>') && lines[i].length > 20) {
                    const m = lines[i].match(/^(.+?)<p>/);
                    if (m) {
                        const author = m[1].trim();
                        // Extract text content from the HTML
                        const htmlPart = lines[i].substring(m[0].length - 3);
                        const tmp = document.createElement('div');
                        tmp.innerHTML = htmlPart;
                        const content = tmp.textContent.trim().substring(0, 200);
                        const key = author + '|' + content.substring(0, 80);
                        if (!seen.has(key) && author.length > 1) {
                            seen.add(key);
                            results.push({ author, content, boosts: '', favorites: '' });
                        }
                    }
                }
            }
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = PostItem()
        item.author = d.get("author", "")
        item.content = d.get("content", "")
        item.boosts = d.get("boosts", "0")
        item.favorites = d.get("favorites", "0")
        result.posts.append(item)

    print(f"\nFound {len(result.posts)} trending posts:")
    for i, p in enumerate(result.posts, 1):
        print(f"\n  {i}. {p.author}")
        print(f"     Content: {p.content[:100]}...")
        print(f"     Boosts: {p.boosts}  Favorites: {p.favorites}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("mastodon")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = browse_mastodon_trending(page, MastodonRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.posts)} posts")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
