"""
Auto-generated Playwright script (Python)
commonsensemedia.org – Game Review Lookup
Game: minecraft

Generated on: 2026-04-18T00:37:43.843Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from playwright.sync_api import Playwright, sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class CSMReviewRequest:
    game_slug: str = "minecraft"


@dataclass(frozen=True)
class CSMReviewResult:
    title: str = ""
    age_rating: str = ""
    quality_rating: str = ""
    one_liner: str = ""
    parents_need_to_know: str = ""


def csm_review(page: Page, request: CSMReviewRequest) -> CSMReviewResult:
    """Look up a game review on Common Sense Media."""
    game_slug = request.game_slug
    print(f"  Game: {game_slug}\n")

    # ── Navigate to game review page ──────────────────────────────────
    url = f"https://www.commonsensemedia.org/game-reviews/{game_slug}"
    print(f"Loading {url}...")
    checkpoint("Navigate to CSM game review page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    # ── Extract review data ───────────────────────────────────────────
    checkpoint("Extract review data")
    data = page.evaluate(r"""() => {
        // Title
        const titleEl = document.querySelector('h1 .heading--sourceserifpro');
        const title = titleEl ? titleEl.textContent.trim() : '';

        // Age rating
        const ratingEls = document.querySelectorAll('.rating__age, .review-rating');
        let ageRating = '';
        for (const el of ratingEls) {
            const t = el.textContent.trim();
            if (/age \d+/i.test(t)) { ageRating = t; break; }
        }

        // Quality stars (first rating__score group)
        const firstScoreEl = document.querySelector('.rating__score');
        let qualityRating = 'N/A';
        if (firstScoreEl) {
            const active = firstScoreEl.querySelectorAll('i.icon-star-solid.active').length;
            const total = firstScoreEl.querySelectorAll('i.icon-star-solid').length;
            qualityRating = active + '/' + total;
        }

        // One-liner and PNTK from body text
        const bodyText = document.body.innerText;
        const oneLinerMatch = bodyText.match(/age \d\+\s*\n\s*(.+?)(?:\n|$)/);
        const oneLiner = oneLinerMatch ? oneLinerMatch[1].trim() : '';

        const pntkMatch = bodyText.match(/Parents [Nn]eed to [Kk]now\s*\n\s*([\s\S]*?)(?:\n\s*\n|\nWhy Age)/);
        const pntkText = pntkMatch ? pntkMatch[1].trim() : '';

        return { title, ageRating, qualityRating, oneLiner, pntkText };
    }""")

    result = CSMReviewResult(
        title=data.get("title", ""),
        age_rating=data.get("ageRating", ""),
        quality_rating=data.get("qualityRating", "N/A"),
        one_liner=data.get("oneLiner", ""),
        parents_need_to_know=data.get("pntkText", ""),
    )

    # ── Print results ─────────────────────────────────────────────────
    print("=" * 60)
    print(f"Common Sense Media – {result.title} Review")
    print("=" * 60)
    print(f"  Title: {result.title}")
    print(f"  Age Rating: {result.age_rating}")
    print(f"  Quality: {result.quality_rating} stars")
    print(f"  Summary: {result.one_liner}")
    print(f"  Parents Need to Know: {result.parents_need_to_know[:300]}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("commonsensemedia_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = csm_review(page, CSMReviewRequest())
            print(f"\nDone: {result.title}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
