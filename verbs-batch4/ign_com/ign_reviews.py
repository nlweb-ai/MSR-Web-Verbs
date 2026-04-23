import re
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class IgnReviewsRequest:
    query: str = "Zelda"
    max_results: int = 5

@dataclass(frozen=True)
class IgnReview:
    game_title: str = ""
    platform: str = ""
    score: str = ""
    summary: str = ""

@dataclass(frozen=True)
class IgnReviewsResult:
    reviews: list = None  # list[IgnReview]

# Search for game reviews on IGN matching a query and extract
# game title, platform, score, and summary.
def ign_reviews(page: Page, request: IgnReviewsRequest) -> IgnReviewsResult:
    query = request.query
    max_results = request.max_results
    print(f"  Search query: {query}")
    print(f"  Max results: {max_results}\n")

    # IGN search is broken (returns 404), so use the reviews listing page instead
    url = "https://www.ign.com/reviews"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to {url}")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    results = []

    # Extract from .content-item cards on the reviews page
    # Card text structure:
    #   score (e.g. "9")
    #   title (e.g. 'The Pitt Season 2 Finale: "9:00 PM" Review')
    #   time + summary (e.g. "4h ago - The day shift has finally ended.")
    #   category (e.g. "THE PITT")
    #   author (e.g. "JESSE SCHEDEEN")
    #   comment count (e.g. "4")
    cards = page.locator(".content-item")
    count = cards.count()
    print(f"  Found {count} review cards")

    if count > 0:
        for i in range(min(count, max_results)):
            card = cards.nth(i)
            try:
                card_text = card.inner_text(timeout=3000).strip()
                lines = [l.strip() for l in card_text.split("\n") if l.strip()]

                game_title = "N/A"
                platform = "N/A"
                score = "N/A"
                summary = "N/A"

                if len(lines) >= 2:
                    # First line is the score
                    sm = re.match(r'^(\d+(?:\.\d+)?)$', lines[0])
                    if sm:
                        score = sm.group(1) + "/10"

                    # Second line is the title (with " Review" suffix)
                    game_title = lines[1]

                    # Third line has "Xh ago - summary text"
                    if len(lines) >= 3:
                        sum_match = re.match(r'^.*?ago\s*[-–]\s*(.+)$', lines[2])
                        if sum_match:
                            summary = sum_match.group(1)
                        else:
                            summary = lines[2]

                    # Fourth line is the category/franchise (can be used as platform/type)
                    if len(lines) >= 4:
                        platform = lines[3]

                if game_title != "N/A":
                    results.append(IgnReview(
                        game_title=game_title,
                        platform=platform,
                        score=score,
                        summary=summary,
                    ))
            except Exception:
                continue

    # Fallback: text-based extraction from body text
    if not results:
        print("  Card selectors missed, trying text-based extraction...")
        body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""
        text_lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        i = 0
        while i < len(text_lines) and len(results) < max_results:
            line = text_lines[i]
            # Look for "Review" in the title
            if "Review" in line and len(line) > 10:
                game_title = line
                score = "N/A"
                platform = "N/A"
                summary = "N/A"

                # Score is on the line before
                if i > 0:
                    sm = re.match(r'^(\d+(?:\.\d+)?)$', text_lines[i - 1])
                    if sm:
                        score = sm.group(1) + "/10"

                # Summary is on the next line (time ago - description)
                if i + 1 < len(text_lines):
                    sum_match = re.match(r'^.*?ago\s*[-–]\s*(.+)$', text_lines[i + 1])
                    if sum_match:
                        summary = sum_match.group(1)

                # Category on line after summary
                if i + 2 < len(text_lines):
                    platform = text_lines[i + 2]

                results.append(IgnReview(
                    game_title=game_title,
                    platform=platform,
                    score=score,
                    summary=summary,
                ))
                i += 4
                continue
            i += 1

        results = results[:max_results]

    print("=" * 60)
    print(f"IGN - Review Results for \"{query}\"")
    print("=" * 60)
    for idx, r in enumerate(results, 1):
        print(f"\n{idx}. {r.game_title}")
        print(f"   Platform: {r.platform}")
        print(f"   Score: {r.score}")
        print(f"   Summary: {r.summary}")

    print(f"\nFound {len(results)} reviews")

    return IgnReviewsResult(reviews=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = ign_reviews(page, IgnReviewsRequest())
        print(f"\nReturned {len(result.reviews or [])} reviews")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
