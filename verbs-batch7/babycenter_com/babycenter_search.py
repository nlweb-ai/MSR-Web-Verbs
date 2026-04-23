"""
Auto-generated Playwright script (Python)
BabyCenter – Article Search
Topic: "baby sleep training"

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
class ArticleSearchRequest:
    search_topic: str = "baby sleep training"
    topic_slug: str = "baby/sleep"
    max_articles: int = 5


@dataclass
class Article:
    title: str = ""
    author: str = ""
    summary: str = ""
    url: str = ""


@dataclass
class ArticleSearchResult:
    articles: List[Article] = field(default_factory=list)


def babycenter_search(page: Page, request: ArticleSearchRequest) -> ArticleSearchResult:
    """Search BabyCenter for articles on a topic."""
    print(f"  Topic: {request.search_topic}\n")

    # ── Navigate to topic page ────────────────────────────────────────
    url = f"https://www.babycenter.com/{request.topic_slug}"
    print(f"Loading {url}...")
    checkpoint("Navigate to BabyCenter topic page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    # ── Dismiss consent dialog ────────────────────────────────────────
    try:
        consent = page.locator("text=I Consent")
        if consent.is_visible(timeout=3000):
            consent.click()
            page.wait_for_timeout(2000)
    except Exception:
        pass

    result = ArticleSearchResult()

    # ── Extract article links from topic page ─────────────────────────
    checkpoint("Extract article list")
    raw_articles = page.evaluate("""(topicSlug) => {
        const results = [];
        document.querySelectorAll('a').forEach(a => {
            const href = a.getAttribute('href') || '';
            const text = a.innerText.trim();
            if (text.length > 10 && text.length < 300 && href.includes('/' + topicSlug + '/') && href !== '/' + topicSlug) {
                const parts = text.split('\\n').map(s => s.trim()).filter(Boolean);
                const title = parts[0] || '';
                let author = '';
                for (const p of parts) {
                    if (p.startsWith('Reviewed by') || p.startsWith('By ')) {
                        author = p;
                        break;
                    }
                }
                if (title && !results.some(r => r.title === title)) {
                    results.push({title, author, href});
                }
            }
        });
        return results;
    }""", request.topic_slug)

    # ── Visit each article to get summary ─────────────────────────────
    for i, raw in enumerate(raw_articles[:request.max_articles]):
        article = Article()
        article.title = raw["title"]
        article.author = raw.get("author", "")
        article.url = "https://www.babycenter.com" + raw["href"]

        checkpoint(f"Visit article {i+1}")
        try:
            page.goto(article.url, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)

            # Dismiss consent again if needed
            try:
                consent = page.locator("text=I Consent")
                if consent.is_visible(timeout=1000):
                    consent.click()
                    page.wait_for_timeout(1000)
            except Exception:
                pass

            # Extract first paragraph as summary
            summary = page.evaluate("""() => {
                const ps = document.querySelectorAll('p');
                for (const p of ps) {
                    const t = p.innerText.trim();
                    if (t.length > 50 && !t.includes('Advertisement')) {
                        return t;
                    }
                }
                return '';
            }""")
            article.summary = summary[:300] if summary else ""
        except Exception:
            pass

        result.articles.append(article)

    # ── Print results ─────────────────────────────────────────────────
    for i, a in enumerate(result.articles, 1):
        print(f"\n  Article {i}:")
        print(f"    Title:   {a.title}")
        print(f"    Author:  {a.author}")
        print(f"    URL:     {a.url}")
        print(f"    Summary: {a.summary[:100]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("babycenter")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = ArticleSearchRequest()
            result = babycenter_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
