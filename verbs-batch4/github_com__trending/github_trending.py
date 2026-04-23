import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class GithubTrendingRequest:
    language: str = "python"
    since: str = "weekly"
    max_results: int = 10

@dataclass(frozen=True)
class TrendingRepo:
    repo_name: str = ""
    description: str = ""
    language: str = ""
    total_stars: str = ""
    stars_this_week: str = ""

@dataclass(frozen=True)
class GithubTrendingResult:
    repos: list = None  # list[TrendingRepo]

# Browse GitHub Trending repositories filtered by language and date range,
# and extract repo name, description, language, total stars, and stars this period.
def github_trending(page: Page, request: GithubTrendingRequest) -> GithubTrendingResult:
    language = request.language.lower()
    since = request.since.lower()
    max_results = request.max_results
    print(f"  Language: {language}")
    print(f"  Since: {since}")
    print(f"  Max results: {max_results}\n")

    url = f"https://github.com/trending/{language}?since={since}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to GitHub Trending")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""

    results = []

    # Try structured extraction via repo row elements
    rows = page.locator('article.Box-row')
    count = rows.count()
    print(f"  Found {count} trending repo rows via selectors")

    if count > 0:
        for i in range(min(count, max_results)):
            row = rows.nth(i)
            try:
                row_text = row.inner_text(timeout=3000).strip()
                lines = [l.strip() for l in row_text.split("\n") if l.strip()]

                repo_name = ""
                description = ""
                lang = ""
                total_stars = ""
                stars_period = ""

                # Extract repo name from the h2 > a link
                name_el = row.locator("h2 a")
                if name_el.count() > 0:
                    raw = name_el.first.inner_text(timeout=2000).strip()
                    # Normalize "owner / repo" -> "owner/repo"
                    repo_name = re.sub(r'\s*/\s*', '/', raw).strip()

                # Extract description from <p> element
                desc_el = row.locator("p")
                if desc_el.count() > 0:
                    description = desc_el.first.inner_text(timeout=2000).strip()

                # Parse stars, language, and period stars from row text
                # Total stars pattern: e.g. "12,345" or "1,234"
                star_matches = re.findall(r'([\d,]+)\s*(?:stars?)?', row_text)

                # Stars this week/today/month pattern
                period_match = re.search(
                    r'([\d,]+)\s+stars?\s+(?:this\s+)?(today|this week|this month|week|month|day)',
                    row_text, re.IGNORECASE
                )
                if period_match:
                    stars_period = period_match.group(1) + " " + period_match.group(2)

                # Language from span with itemprop or class
                lang_el = row.locator('[itemprop="programmingLanguage"]')
                if lang_el.count() > 0:
                    lang = lang_el.first.inner_text(timeout=2000).strip()

                # Total stars from the link that points to stargazers
                star_link = row.locator('a[href*="/stargazers"]')
                if star_link.count() > 0:
                    total_stars = star_link.first.inner_text(timeout=2000).strip().replace(",", "").strip()
                    # Re-format with commas if numeric
                    try:
                        total_stars = f"{int(total_stars):,}"
                    except ValueError:
                        pass

                if repo_name:
                    results.append(TrendingRepo(
                        repo_name=repo_name,
                        description=description,
                        language=lang,
                        total_stars=total_stars,
                        stars_this_week=stars_period,
                    ))
            except Exception:
                continue

    # Fallback: text-based extraction
    if not results:
        print("  Selector extraction missed, trying text-based extraction...")
        text_lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        i = 0
        while i < len(text_lines) and len(results) < max_results:
            line = text_lines[i]
            # Repo name pattern: "owner / repo" or "owner/repo"
            repo_match = re.match(r'^([\w._-]+)\s*/\s*([\w._-]+)$', line)
            if repo_match:
                repo_name = f"{repo_match.group(1)}/{repo_match.group(2)}"
                description = ""
                lang = ""
                total_stars = ""
                stars_period = ""

                # Scan next lines for description, language, stars
                for j in range(i + 1, min(len(text_lines), i + 12)):
                    nearby = text_lines[j]

                    # Stars this period
                    pm = re.search(
                        r'([\d,]+)\s+stars?\s+(?:this\s+)?(today|this week|this month|week|month|day)',
                        nearby, re.IGNORECASE
                    )
                    if pm:
                        stars_period = pm.group(1) + " " + pm.group(2)
                        continue

                    # Pure number likely total stars
                    sm = re.match(r'^([\d,]+)$', nearby)
                    if sm and not total_stars:
                        total_stars = sm.group(1)
                        continue

                    # Short language name
                    if (len(nearby) < 25 and not re.match(r'^[\d,]+$', nearby)
                            and nearby.lower() not in ("star", "stars", "built by", "sponsored")
                            and not lang):
                        lang = nearby
                        continue

                    # Description — longer text line
                    if len(nearby) > 20 and not description and not re.match(r'^[\d,]+$', nearby):
                        description = nearby

                if repo_name:
                    results.append(TrendingRepo(
                        repo_name=repo_name,
                        description=description,
                        language=lang,
                        total_stars=total_stars,
                        stars_this_week=stars_period,
                    ))
                i += 10
                continue
            i += 1

        results = results[:max_results]

    print("=" * 60)
    print(f"GitHub Trending — {language.title()} ({since})")
    print("=" * 60)
    for idx, r in enumerate(results, 1):
        print(f"\n{idx}. {r.repo_name}")
        print(f"   Description: {r.description}")
        print(f"   Language: {r.language}")
        print(f"   Total Stars: {r.total_stars}")
        print(f"   Stars This Period: {r.stars_this_week}")

    print(f"\nFound {len(results)} trending repos")

    return GithubTrendingResult(repos=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = github_trending(page, GithubTrendingRequest())
        print(f"\nReturned {len(result.repos or [])} repos")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
