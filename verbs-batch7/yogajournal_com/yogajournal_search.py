"""
Auto-generated Playwright script (Python)
Yoga Journal – Pose/Article Search

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
class SearchRequest:
    search_query: str = "warrior pose"
    max_results: int = 5


@dataclass
class ArticleResult:
    category: str = ""
    title: str = ""
    summary: str = ""
    author: str = ""
    date: str = ""


@dataclass
class SearchResult:
    articles: List[ArticleResult] = field(default_factory=list)


def yogajournal_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search Yoga Journal for articles/poses."""
    print(f"  Query: {request.search_query}\n")

    query_encoded = request.search_query.replace(" ", "+")
    url = f"https://www.yogajournal.com/?s={query_encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(8000)

    result = SearchResult()

    checkpoint("Extract search results")
    js_code = r"""(max) => {
        const lines = document.body.innerText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        const articles = [];
        // Find start - after "Displaying X - Y of approximately Z results"
        let i = 0;
        for (; i < lines.length; i++) {
            if (lines[i].startsWith('Displaying ') && lines[i].includes('results')) { i++; break; }
        }
        // Pattern: category, title, summary (optional), author, date
        // Categories are short known phrases
        const categories = new Set(['Practice Yoga', 'Beginner Yoga Poses', 'Balancing Yoga Poses',
            'How-To Yoga Videos', 'Intermediate Yoga Poses', 'Advanced Yoga Poses',
            'Yoga Sequences', 'Teach', 'Meditation', 'Lifestyle', 'Foundations',
            'Featured', 'Poses', 'Accessories', 'Astrology', 'Pose Finder',
            'Standing Yoga Poses', 'Seated Yoga Poses', 'Restorative Yoga Poses',
            'Arm Balance Yoga Poses', 'Core Yoga Poses', 'Backbend Yoga Poses',
            'Hip-Opening Yoga Poses', 'Twist Yoga Poses', 'Inversion Yoga Poses',
            'Forward Bend Yoga Poses', 'Yoga Anatomy']);
        while (i < lines.length && articles.length < max) {
            // Expect category
            let category = '';
            if (categories.has(lines[i])) {
                category = lines[i]; i++;
            }
            if (i >= lines.length) break;
            const title = lines[i]; i++;
            // Check if next line is summary or author
            let summary = '';
            if (i < lines.length && !lines[i].startsWith('Published ') && !lines[i].startsWith('Updated ') &&
                !lines[i].startsWith('Check out ') && lines[i].length > 40) {
                summary = lines[i]; i++;
            } else if (i < lines.length && lines[i].startsWith('Check out ')) {
                i++; // skip "Check out X's author page."
            }
            // Author
            let author = '';
            if (i < lines.length && !lines[i].startsWith('Published ') && !lines[i].startsWith('Updated ') &&
                !categories.has(lines[i])) {
                author = lines[i]; i++;
            }
            // Date
            let date = '';
            if (i < lines.length && (lines[i].startsWith('Published ') || lines[i].startsWith('Updated '))) {
                date = lines[i]; i++;
            }
            if (title && title.length > 5) {
                articles.push({category, title, summary, author, date});
            }
        }
        return articles;
    }"""
    articles_data = page.evaluate(js_code, request.max_results)

    for ad in articles_data:
        a = ArticleResult()
        a.category = ad.get("category", "")
        a.title = ad.get("title", "")
        a.summary = ad.get("summary", "")
        a.author = ad.get("author", "")
        a.date = ad.get("date", "")
        result.articles.append(a)

    for i, a in enumerate(result.articles, 1):
        print(f"\n  Article {i}:")
        print(f"    Category: {a.category}")
        print(f"    Title:    {a.title}")
        print(f"    Summary:  {a.summary[:80]}..." if a.summary else "    Summary:  (none)")
        print(f"    Author:   {a.author}")
        print(f"    Date:     {a.date}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("yogajournal")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = yogajournal_search(page, request)
            print(f"\n=== DONE ===")
            print(f"Found {len(result.articles)} articles")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
