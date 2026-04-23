"""
Quizlet – Search for study sets by keyword

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
class QuizletSearchRequest:
    search_query: str = "biology"
    max_results: int = 5


@dataclass
class QuizletSetItem:
    set_title: str = ""
    creator: str = ""
    num_terms: str = ""
    num_learners: str = ""
    rating: str = ""
    subject: str = ""


@dataclass
class QuizletSearchResult:
    items: List[QuizletSetItem] = field(default_factory=list)


# Search for study sets on Quizlet by keyword.
def quizlet_search(page: Page, request: QuizletSearchRequest) -> QuizletSearchResult:
    """Search for study sets on Quizlet."""
    print(f"  Query: {request.search_query}\n")

    query = request.search_query.replace(" ", "+")
    url = f"https://quizlet.com/search?query={query}&type=sets"
    print(f"Loading {url}...")
    checkpoint("Navigate to Quizlet search results")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = QuizletSearchResult()

    checkpoint("Extract study set listings")
    js_code = """(max) => {
        const cards = document.querySelectorAll('[class*="SearchResult"], [class*="set-card"], [class*="SetResult"], [class*="result"], [data-testid*="result"]');
        const items = [];
        for (const card of cards) {
            if (items.length >= max) break;
            const titleEl = card.querySelector('h2, h3, [class*="title"], [class*="SetTitle"], a[class*="title"]');
            const creatorEl = card.querySelector('[class*="creator"], [class*="author"], [class*="user"], [class*="byline"]');
            const termsEl = card.querySelector('[class*="term"], [class*="count"], [class*="numTerms"]');
            const learnersEl = card.querySelector('[class*="learner"], [class*="student"], [class*="studied"]');
            const ratingEl = card.querySelector('[class*="rating"], [class*="star"], [class*="score"]');
            const subjectEl = card.querySelector('[class*="subject"], [class*="category"], [class*="topic"], [class*="label"]');

            const set_title = titleEl ? titleEl.textContent.trim() : '';
            const creator = creatorEl ? creatorEl.textContent.trim() : '';
            const num_terms = termsEl ? termsEl.textContent.trim() : '';
            const num_learners = learnersEl ? learnersEl.textContent.trim() : '';
            const rating = ratingEl ? ratingEl.textContent.trim() : '';
            const subject = subjectEl ? subjectEl.textContent.trim() : '';

            if (set_title) {
                items.push({set_title, creator, num_terms, num_learners, rating, subject});
            }
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = QuizletSetItem()
        item.set_title = d.get("set_title", "")
        item.creator = d.get("creator", "")
        item.num_terms = d.get("num_terms", "")
        item.num_learners = d.get("num_learners", "")
        item.rating = d.get("rating", "")
        item.subject = d.get("subject", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Study Set {i}:")
        print(f"    Title:    {item.set_title}")
        print(f"    Creator:  {item.creator}")
        print(f"    Terms:    {item.num_terms}")
        print(f"    Learners: {item.num_learners}")
        print(f"    Rating:   {item.rating}")
        print(f"    Subject:  {item.subject}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("quizlet")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = QuizletSearchRequest()
            result = quizlet_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} study sets")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
