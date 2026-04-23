"""
Playwright script (Python) — IMDb TV Show Info
Search for a TV show, extract rating, seasons, and top episodes.

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ImdbTvShowRequest:
    show_name: str
    max_episodes: int


@dataclass(frozen=True)
class ImdbEpisode:
    title: str
    episode: str
    rating: str


@dataclass(frozen=True)
class ImdbTvShowResult:
    show_name: str
    show_rating: str
    num_seasons: str
    top_episodes: list[ImdbEpisode]


# Searches IMDb for a TV show and extracts show rating, number of seasons,
# and up to max_episodes top episodes with title, episode number, and rating.
def search_imdb_tvshow(
    page: Page,
    request: ImdbTvShowRequest,
) -> ImdbTvShowResult:
    show_name = request.show_name
    max_episodes = request.max_episodes

    print(f"  Show: {show_name}")
    print(f"  Max episodes: {max_episodes}\n")

    show_rating = "N/A"
    num_seasons = "N/A"
    episodes: list[ImdbEpisode] = []

    try:
        print("Loading IMDb...")
        checkpoint("Navigate to https://www.imdb.com")
        page.goto("https://www.imdb.com")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        for sel in ["button#onetrust-accept-btn-handler", "button:has-text('Accept')", "button:has-text('Close')"]:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=1500):
                    checkpoint(f"Dismiss popup: {sel}")
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        print(f'STEP 1: Search for "{show_name}"...')
        search_input = page.locator('input[name="q"], input[id="suggestion-search"], input[aria-label*="search" i]').first
        checkpoint("Click search input")
        search_input.evaluate("el => el.click()")
        page.wait_for_timeout(500)
        page.keyboard.press("Control+a")
        checkpoint(f"Type show name: {show_name}")
        search_input.type(show_name, delay=50)
        page.wait_for_timeout(2000)
        try:
            suggestion = page.locator('[data-testid="search-result--const"] a, li[role="option"] a').first
            suggestion.wait_for(state="visible", timeout=3000)
            checkpoint("Click first search suggestion")
            suggestion.evaluate("el => el.click()")
        except Exception:
            checkpoint("Press Enter to search")
            page.keyboard.press("Enter")
        page.wait_for_timeout(2000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)

        print("STEP 2: Extract show info...")
        try:
            rating_el = page.locator('[data-testid="hero-rating-bar__aggregate-rating__score"] span, span[class*="rating"]').first
            show_rating = rating_el.inner_text(timeout=3000).strip()
        except Exception:
            pass
        try:
            text = page.locator('[data-testid="episodes-header"]').inner_text(timeout=3000)
            m = re.search(r"(\d+)\s*[Ss]eason", text)
            if m:
                num_seasons = m.group(1)
        except Exception:
            pass

        print(f"STEP 3: Extract top {max_episodes} episodes...")
        try:
            ep_link = page.locator('a[href*="episodes"], a:has-text("Episodes")').first
            checkpoint("Click Episodes link")
            ep_link.evaluate("el => el.click()")
            page.wait_for_timeout(2000)
        except Exception:
            pass

        ep_items = page.locator('[data-testid="episode-card"], article[class*="episode"], div[class*="episode"]')
        count = ep_items.count()
        print(f"  Found {count} episodes")

        for i in range(min(count, max_episodes)):
            item = ep_items.nth(i)
            try:
                title = ep_num = rating = "N/A"
                try:
                    title = item.locator('a[class*="title"], h4, [data-testid="slate-text"]').first.inner_text(timeout=2000).strip()
                except Exception:
                    pass
                try:
                    ep_num = item.locator('[class*="episode-number"], [class*="ep-num"]').first.inner_text(timeout=2000).strip()
                except Exception:
                    pass
                try:
                    rating_text = item.locator('[class*="rating"], [data-testid*="rating"]').first.inner_text(timeout=2000).strip()
                    m = re.search(r"([\d.]+)", rating_text)
                    if m:
                        rating = m.group(1)
                except Exception:
                    pass
                if title != "N/A":
                    episodes.append(ImdbEpisode(title=title, episode=ep_num, rating=rating))
                    print(f"  {len(episodes)}. {title} | {ep_num} | Rating: {rating}")
            except Exception as e:
                print(f"  Error: {e}")

        print(f"\nShow: {show_name}")
        print(f"  Rating: {show_rating}  Seasons: {num_seasons}")
        for i, ep in enumerate(episodes, 1):
            print(f"  {i}. {ep.title} ({ep.episode}) — {ep.rating}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return ImdbTvShowResult(show_name=show_name, show_rating=show_rating, num_seasons=num_seasons, top_episodes=episodes)


def test_search_imdb_tvshow() -> None:
    request = ImdbTvShowRequest(show_name="Breaking Bad", max_episodes=5)
    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir, channel="chrome", headless=False, viewport=None,
            args=["--disable-blink-features=AutomationControlled", "--disable-infobars", "--disable-extensions"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_imdb_tvshow(page, request)
            assert result.show_name == request.show_name
            assert len(result.top_episodes) <= request.max_episodes
            print(f"\nTotal episodes found: {len(result.top_episodes)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_imdb_tvshow)
