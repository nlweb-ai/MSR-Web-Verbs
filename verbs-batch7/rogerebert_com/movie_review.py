"""
RogerEbert.com – Movie Review Lookup

Navigate to a specific movie review page on RogerEbert.com and extract
the title, star rating, review date, author, and opening paragraph.
"""

import os, sys, re, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws


@dataclass(frozen=True)
class Request:
    movie_slug: str = "parasite-movie-review-2019"


@dataclass
class Result:
    title: str = ""
    star_rating: str = ""
    review_date: str = ""
    author: str = ""
    opening_paragraph: str = ""


def movie_review(page, request: Request) -> Result:
    """Navigate to a RogerEbert.com review and extract details."""
    url = f"https://www.rogerebert.com/reviews/{request.movie_slug}"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    data = page.evaluate(r"""() => {
        // Title
        const h1 = document.querySelector('h1');
        const title = h1 ? h1.textContent.trim() : '';

        // Star rating from CSS class on the filled star image
        const filledImg = document.querySelector('.star-box .filled');
        let starRating = '';
        if (filledImg) {
            const m = filledImg.className.match(/star(\d+)/);
            if (m) starRating = (parseInt(m[1]) / 10).toFixed(1);
        }

        // Navigate up from star-box to find the review section
        const starBox = document.querySelector('.star-box');
        let section = starBox;
        if (section) {
            for (let i = 0; i < 8; i++) {
                if (section.parentElement) section = section.parentElement;
            }
        }
        const sectionText = section ? section.innerText : document.body.innerText;

        // Review date
        const dateMatch = sectionText.match(
            /(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}/
        );
        const reviewDate = dateMatch ? dateMatch[0] : '';

        // Author
        let author = '';
        if (section) {
            const authorLink = section.querySelector('a[href*="/contributors/"], a[href*="/author/"]');
            if (authorLink) author = authorLink.textContent.trim();
        }
        if (!author) {
            const lines = sectionText.split('\n').map(l => l.trim()).filter(Boolean);
            for (const line of lines) {
                if (/^[A-Z][a-z]+ [A-Z][a-z]+$/.test(line)) { author = line; break; }
            }
        }

        // First paragraph of review text (first <p> with >100 chars)
        const paragraphs = document.querySelectorAll('p');
        let opening = '';
        for (const p of paragraphs) {
            const t = p.textContent.trim();
            if (t.length > 100) { opening = t; break; }
        }

        return { title, starRating, reviewDate, author, opening };
    }""")

    return Result(
        title=data.get("title", ""),
        star_rating=data.get("starRating", ""),
        review_date=data.get("reviewDate", ""),
        author=data.get("author", ""),
        opening_paragraph=data.get("opening", ""),
    )


# ── Test ──────────────────────────────────────────────────────────────────────
def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("rogerebert_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            req = Request(movie_slug="parasite-movie-review-2019")
            result = movie_review(page, req)
            print(f"\n=== RogerEbert.com Review ===")
            print(f"  Title:    {result.title}")
            print(f"  Rating:   {result.star_rating}/4")
            print(f"  Date:     {result.review_date}")
            print(f"  Author:   {result.author}")
            print(f"  Opening:  {result.opening_paragraph[:200]}...")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
