"""
NYTimes – Search "artificial intelligence" → sort Newest → extract top 5 articles.
Pure Playwright – no AI.
"""
import re, os, sys, traceback, shutil, tempfile
from playwright.sync_api import Page, sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, launch_chrome, wait_for_cdp_ws, find_chrome_executable
from playwright_debugger import checkpoint

from dataclasses import dataclass
import subprocess
import json
import time
from urllib.request import urlopen


@dataclass(frozen=True)
class NYTimesSearchRequest:
    query: str = "artificial intelligence"
    max_results: int = 5


@dataclass(frozen=True)
class NYTimesArticle:
    headline: str
    author: str
    date: str


@dataclass(frozen=True)
class NYTimesSearchResult:
    query: str
    articles: list


def search_nytimes_articles(page: Page, request: NYTimesSearchRequest) -> NYTimesSearchResult:
    articles = []
    try:
        # Use the search URL directly with sort=newest
        print("STEP 1: Navigate to NYTimes search for 'artificial intelligence' sorted by newest...")
        checkpoint("Navigate to NYTimes search for artificial intelligence sorted by newest")
        page.goto(
            "https://www.nytimes.com/search?query=artificial+intelligence&sort=newest",
            wait_until="domcontentloaded", timeout=30000,
        )
        page.wait_for_timeout(5000)

        # Dismiss cookie / GDPR banners
        for sel in ["button:has-text('Accept')", "button:has-text('Continue')",
                     "button:has-text('I Accept')", "button[data-testid='GDPR-accept']",
                     "button:has-text('Agree')"]:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=800):
                    checkpoint("Click dismiss banner button")
                    loc.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        # Scroll to load results
        for _ in range(3):
            page.evaluate("window.scrollBy(0, 800)")
            page.wait_for_timeout(1000)

        print("STEP 2: Extract articles...")

        # Strategy 1: search result list items
        seen = set()
        result_items = page.locator("li[data-testid='search-bodega-result']").all()
        if not result_items:
            result_items = page.locator("ol[data-testid='search-results'] li").all()
        if not result_items:
            result_items = page.locator("[data-testid='search-results'] li").all()

        print(f"   Found {len(result_items)} search result elements")

        for item in result_items:
            if len(articles) >= request.max_results:
                break
            try:
                text = item.inner_text(timeout=2000).strip()
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                if len(lines) < 2:
                    continue

                headline = ""
                author = ""
                date = ""

                # First substantial line is usually the headline
                for ln in lines:
                    if len(ln) > 15 and not re.match(r'^(By |[A-Z][a-z]+\.\s+\d)', ln):
                        headline = ln
                        break
                if not headline and lines:
                    headline = lines[0]

                # Look for "By Author" pattern
                for ln in lines:
                    if ln.startswith("By "):
                        author = ln
                        break

                # Look for date pattern like "Jan. 15, 2025", "March 8, 2026", or "2 hours ago"
                for ln in lines:
                    if re.match(r'^[A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4}', ln):
                        date = ln
                        break
                    if re.search(r'\d+\s+(hour|minute|day|week)s?\s+ago', ln):
                        date = ln
                        break
                    if re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', ln):
                        date = ln
                        break

                key = headline.lower()[:50]
                if key in seen:
                    continue
                seen.add(key)
                articles.append({
                    "headline": headline,
                    "author": author or "N/A",
                    "date": date or "N/A",
                })
            except Exception:
                continue

        # Strategy 2: body text fallback
        if not articles:
            print("   Strategy 1 found 0 — trying body text...")
            body = page.inner_text("body")
            lines = [l.strip() for l in body.splitlines() if l.strip()]
            i = 0
            while i < len(lines) and len(articles) < request.max_results:
                # Look for a line that looks like a headline (long text)
                if len(lines[i]) > 30 and not lines[i].startswith("By "):
                    headline = lines[i]
                    author = ""
                    date = ""
                    # Check next few lines for author/date
                    for j in range(i + 1, min(i + 5, len(lines))):
                        if lines[j].startswith("By "):
                            author = lines[j]
                        if re.match(r'^[A-Z][a-z]+\.?\s+\d{1,2},\s+\d{4}', lines[j]):
                            date = lines[j]
                    if author or date:
                        key = headline.lower()[:50]
                        if key not in seen:
                            seen.add(key)
                            articles.append({
                                "headline": headline,
                                "author": author or "N/A",
                                "date": date or "N/A",
                            })
                i += 1

        if not articles:
            print("❌ ERROR: Extraction failed — no articles found from the page.")

        print(f"\nDONE – Top {len(articles)} NYTimes Articles (sorted newest):")
        for i, a in enumerate(articles, 1):
            print(f"  {i}. {a['headline']}")
            print(f"     {a['author']}  |  {a['date']}")

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    return NYTimesSearchResult(
        query=request.query,
        articles=[NYTimesArticle(headline=a['headline'], author=a['author'], date=a['date']) for a in articles],
    )


def test_nytimes_articles():
    from playwright.sync_api import sync_playwright
    request = NYTimesSearchRequest(query="artificial intelligence", max_results=5)
    port = get_free_port()
    profile_dir = tempfile.mkdtemp(prefix="chrome_cdp_")
    chrome = os.environ.get("CHROME_PATH") or find_chrome_executable()
    chrome_proc = subprocess.Popen(
        [
            chrome,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={profile_dir}",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1280,987",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    ws_url = None
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            resp = urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2)
            ws_url = json.loads(resp.read()).get("webSocketDebuggerUrl", "")
            if ws_url:
                break
        except Exception:
            pass
        time.sleep(0.4)
    if not ws_url:
        raise TimeoutError("Chrome CDP not ready")
    with sync_playwright() as pl:
        browser = pl.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_nytimes_articles(page, request)
        finally:
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)
    print(f"\nTotal articles: {len(result.articles)}")
    for i, a in enumerate(result.articles, 1):
        print(f"  {i}. {a.headline}")


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_nytimes_articles)