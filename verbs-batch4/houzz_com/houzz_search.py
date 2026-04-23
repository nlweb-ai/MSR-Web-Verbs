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
class HouzzSearchRequest:
    query: str = "modern kitchen remodel"
    max_results: int = 5

@dataclass(frozen=True)
class HouzzProject:
    title: str = ""
    style: str = ""
    saves: str = ""
    description: str = ""

@dataclass(frozen=True)
class HouzzSearchResult:
    projects: list = None  # list[HouzzProject]

# Search for home renovation ideas on Houzz matching a query and extract
# project title, style, saves, and description.
def houzz_search(page: Page, request: HouzzSearchRequest) -> HouzzSearchResult:
    query = request.query
    max_results = request.max_results
    print(f"  Search query: {query}")
    print(f"  Max results: {max_results}\n")

    url = f"https://www.houzz.com/photos/query/{quote_plus(query)}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to {url}")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""

    results = []

    # Try structured extraction via photo/project card elements
    cards = page.locator(
        '[class*="photo-card"], '
        '[class*="PhotoCard"], '
        '[class*="GalleryCard"], '
        '[class*="gallery-card"], '
        '[data-testid*="photo"], '
        'a[href*="/photo/"]'
    )
    count = cards.count()
    print(f"  Found {count} project cards via selectors")

    if count > 0:
        for i in range(min(count, max_results)):
            card = cards.nth(i)
            try:
                card_text = card.inner_text(timeout=3000).strip()
                lines = [l.strip() for l in card_text.split("\n") if l.strip()]

                title = "N/A"
                style = "N/A"
                saves = "N/A"
                description = "N/A"

                for line in lines:
                    # Saves count — number possibly followed by "saves" or standalone
                    sm = re.search(r'^([\d,]+)\s*(?:saves?|Saves?)?$', line)
                    if sm and saves == "N/A":
                        saves = sm.group(1)
                        continue
                    # Style keywords
                    style_kw = re.search(
                        r'(modern|traditional|contemporary|transitional|rustic|'
                        r'farmhouse|industrial|minimalist|scandinavian|eclectic|'
                        r'coastal|craftsman|mediterranean|mid-century)',
                        line, re.IGNORECASE
                    )
                    if style_kw and style == "N/A":
                        style = style_kw.group(1).title()
                    # Title — longest descriptive line
                    if len(line) > 3 and not re.match(r'^[\d,]+$', line):
                        if title == "N/A" or len(line) > len(title):
                            if title != "N/A" and description == "N/A":
                                description = title
                            title = line

                if title != "N/A":
                    results.append(HouzzProject(
                        title=title,
                        style=style,
                        saves=saves,
                        description=description,
                    ))
            except Exception:
                continue

    # Fallback: text-based extraction
    if not results:
        print("  Card selectors missed, trying text-based extraction...")
        text_lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        i = 0
        while i < len(text_lines) and len(results) < max_results:
            line = text_lines[i]
            # Look for lines that could be project titles (longer descriptive text)
            if len(line) > 10 and not re.match(r'^[\d,.$%]+$', line):
                title = line
                style = "N/A"
                saves = "N/A"
                description = "N/A"

                # Check nearby lines for style and stats
                for j in range(i + 1, min(len(text_lines), i + 6)):
                    nearby = text_lines[j]
                    # Numeric-only lines are likely save counts
                    nm = re.match(r'^([\d,]+[kKmM]?)$', nearby)
                    if nm:
                        if saves == "N/A":
                            saves = nm.group(1)
                        continue
                    # Style keywords
                    style_kw = re.search(
                        r'(modern|traditional|contemporary|transitional|rustic|'
                        r'farmhouse|industrial|minimalist|scandinavian|eclectic|'
                        r'coastal|craftsman|mediterranean|mid-century)',
                        nearby, re.IGNORECASE
                    )
                    if style_kw and style == "N/A":
                        style = style_kw.group(1).title()
                    # Short descriptive line as description
                    if (len(nearby) > 5 and len(nearby) < 200
                            and not re.match(r'^[\d,]+$', nearby)
                            and description == "N/A"):
                        description = nearby

                if title != "N/A":
                    results.append(HouzzProject(
                        title=title,
                        style=style,
                        saves=saves,
                        description=description,
                    ))
                    i += 5
                    continue
            i += 1

        # Trim to max_results
        results = results[:max_results]

    print("=" * 60)
    print(f"Houzz - Search Results for \"{query}\"")
    print("=" * 60)
    for idx, p in enumerate(results, 1):
        print(f"\n{idx}. {p.title}")
        print(f"   Style: {p.style}")
        print(f"   Saves: {p.saves}")
        print(f"   Description: {p.description}")

    print(f"\nFound {len(results)} projects")

    return HouzzSearchResult(projects=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = houzz_search(page, HouzzSearchRequest())
        print(f"\nReturned {len(result.projects or [])} projects")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
