import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class DuolingoCoursesRequest:
    max_results: int = 10

@dataclass(frozen=True)
class DuolingoCourse:
    language_name: str = ""
    num_learners: str = ""

@dataclass(frozen=True)
class DuolingoCoursesResult:
    courses: list = None  # list[DuolingoCourse]

# Navigate to Duolingo's course catalog page and extract available language
# courses with the language name and number of learners.
def duolingo_courses(page: Page, request: DuolingoCoursesRequest) -> DuolingoCoursesResult:
    max_results = request.max_results
    print(f"  Max courses to extract: {max_results}\n")

    url = "https://www.duolingo.com/courses"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to {url}")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    print(f"  Loaded: {page.url}")

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""

    results = []

    # Try structured extraction via course card elements
    cards = page.locator(
        '[data-test="course-card"], '
        '[class*="course"], '
        'a[href*="/course/"], '
        'div[class*="_card"]'
    )
    count = cards.count()
    print(f"  Found {count} course cards via selectors")

    if count > 0:
        for i in range(min(count, max_results)):
            card = cards.nth(i)
            try:
                card_text = card.inner_text(timeout=3000).strip()
                lines = [l.strip() for l in card_text.split("\n") if l.strip()]

                language_name = "N/A"
                num_learners = "N/A"

                for line in lines:
                    # Number of learners (e.g., "34.2M learners", "12.5 million learners")
                    lm = re.search(r'([\d.,]+\s*[MmKkBb]?(?:illion)?)\s*learner', line, re.I)
                    if lm:
                        num_learners = line.strip()
                        continue
                    # Language name: non-numeric line with reasonable length
                    if (len(line) > 1 and len(line) < 50
                            and not re.match(r'^[\d$%]', line)
                            and language_name == "N/A"):
                        language_name = line

                if language_name != "N/A":
                    results.append(DuolingoCourse(
                        language_name=language_name,
                        num_learners=num_learners,
                    ))
            except Exception:
                continue

    # Fallback: text-based extraction using learner count anchors
    if not results:
        print("  Card selectors missed, trying text-based extraction...")
        text_lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        i = 0
        while i < len(text_lines) and len(results) < max_results:
            line = text_lines[i]
            lm = re.search(r'([\d.,]+\s*[MmKkBb]?(?:illion)?)\s*learner', line, re.I)
            if lm:
                num_learners = line.strip()
                language_name = "N/A"

                # Search nearby lines for a language name
                for j in range(max(0, i - 3), min(len(text_lines), i + 3)):
                    nearby = text_lines[j]
                    if (nearby != line
                            and len(nearby) > 1 and len(nearby) < 50
                            and not re.match(r'^[\d$%]', nearby)
                            and not re.search(r'learner', nearby, re.I)):
                        language_name = nearby
                        break

                if language_name != "N/A":
                    results.append(DuolingoCourse(
                        language_name=language_name,
                        num_learners=num_learners,
                    ))
            i += 1

    print("=" * 60)
    print("Duolingo - Language Courses")
    print("=" * 60)
    for idx, c in enumerate(results, 1):
        print(f"\n{idx}. {c.language_name}")
        print(f"   Learners: {c.num_learners}")

    print(f"\nFound {len(results)} courses")

    return DuolingoCoursesResult(courses=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = duolingo_courses(page, DuolingoCoursesRequest())
        print(f"\nReturned {len(result.courses or [])} courses")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
