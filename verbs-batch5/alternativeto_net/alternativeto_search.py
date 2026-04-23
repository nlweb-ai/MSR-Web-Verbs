"""
Auto-generated Playwright script (Python)
alternativeto.net – Software Alternative Search
Software: Photoshop

Generated on: 2026-04-17T23:47:24.111Z
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
class AlternativeToSearchRequest:
    software_name: str = "Photoshop"
    software_slug: str = "adobe-photoshop"
    max_results: int = 5


@dataclass(frozen=True)
class AlternativeToResult:
    name: str = ""
    description: str = ""
    likes: str = ""
    platforms: str = ""
    pricing: str = ""


@dataclass(frozen=True)
class AlternativeToSearchResult:
    alternatives: list = None  # list[AlternativeToResult]


def alternativeto_search(page: Page, request: AlternativeToSearchRequest) -> AlternativeToSearchResult:
    """Search alternativeto.net for alternatives to a given software."""
    software_name = request.software_name
    software_slug = request.software_slug
    max_results = request.max_results
    print(f"  Software: {software_name}")
    print(f"  Max results: {max_results}\n")

    # ── Navigate to alternatives page ─────────────────────────────────
    url = f"https://alternativeto.net/software/{software_slug}/"
    print(f"Loading {url}...")
    checkpoint("Navigate to alternativeto.net alternatives page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    print(f"  Loaded: {page.url}")

    # ── Dismiss cookie / consent banners ──────────────────────────────
    for selector in [
        "button#onetrust-accept-btn-handler",
        'button:has-text("Accept")',
        'button:has-text("I agree")',
        'button:has-text("Got it")',
    ]:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=1500):
                btn.evaluate("el => el.click()")
                page.wait_for_timeout(500)
                break
        except Exception:
            pass

    # ── Extract alternatives from article elements ────────────────────
    checkpoint("Extract alternatives from article cards")
    articles = page.locator("article")
    count = articles.count()
    print(f"  Found {count} article cards")

    results = []
    for i in range(min(count, max_results)):
        art = articles.nth(i)
        try:
            art_text = art.inner_text(timeout=3000) or ""

            # Name: from a[title^="Learn more about"] → strip prefix
            name = "N/A"
            try:
                title_link = art.locator("a[title]").first
                title_val = title_link.get_attribute("title") or ""
                if title_val.startswith("Learn more about "):
                    name = title_val.replace("Learn more about ", "")
                elif title_val:
                    name = title_val
            except Exception:
                pass

            # Likes: pattern "N likes" in text
            likes = "N/A"
            like_match = re.search(r"(\d+)\s+likes?", art_text)
            if like_match:
                likes = like_match.group(1)

            # Description: from main-app-info, text after likes line
            description = "N/A"
            try:
                info_el = art.locator("[data-testid='main-app-info']").first
                info_text = info_el.inner_text(timeout=2000) or ""
                desc_match = re.search(r"\d+\s+likes?\s*\n\s*([\s\S]+?)(?:\n\d+\s+\w+\s+alternative|$)", info_text)
                if desc_match:
                    description = desc_match.group(1).strip()[:200]
            except Exception:
                pass

            # Pricing: between COST / LICENSE and next section
            pricing = "N/A"
            cost_match = re.search(r"COST\s*/\s*LICENSE\s*\n([\s\S]+?)(?:\nAPPLICATION|\nORIGIN|\nPLATFORMS|\nALERTS|\nMore about)", art_text)
            if cost_match:
                tokens = [re.sub(r"\s*\($", "", t.strip()) for t in cost_match.group(1).strip().split("\n") if t.strip() and t.strip() not in ("(", ")") and not re.match(r"^\(.*\)$", t.strip()) and not re.match(r"^[A-Z]+-[\d.]+$", t.strip())]
                tokens = [t for t in tokens if t]
                if tokens:
                    pricing = " / ".join(tokens)

            # Platforms: from data-testid="platform-row"
            platforms = "N/A"
            try:
                plat_el = art.locator("[data-testid='platform-row']").first
                plat_text = plat_el.inner_text(timeout=2000) or ""
                plats = [t.strip() for t in plat_text.split("\n") if t.strip() and len(t.strip()) < 30 and not re.match(r"^\+\d+$", t.strip())][:6]
                if plats:
                    platforms = ", ".join(plats)
            except Exception:
                pass

            if name != "N/A":
                results.append(AlternativeToResult(
                    name=name,
                    description=description,
                    likes=likes,
                    platforms=platforms,
                    pricing=pricing,
                ))
        except Exception:
            continue

    # ── Print results ─────────────────────────────────────────────────
    print("=" * 60)
    print(f'alternativeto.net - Alternatives to "{software_name}"')
    print("=" * 60)
    for idx, a in enumerate(results, 1):
        print(f"\n{idx}. {a.name}")
        print(f"   Description: {a.description}")
        print(f"   Likes: {a.likes}")
        print(f"   Platforms: {a.platforms}")
        print(f"   Pricing: {a.pricing}")

    print(f"\nFound {len(results)} alternatives")
    return AlternativeToSearchResult(alternatives=results)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("alternativeto_net")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = alternativeto_search(page, AlternativeToSearchRequest())
            print(f"\nReturned {len(result.alternatives or [])} alternatives")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
