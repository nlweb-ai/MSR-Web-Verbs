"""
Playwright script (Python) — Codecademy Course Search
Query: Python   Max results: 5

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
class CodecademySearchRequest:
    query: str
    max_results: int


@dataclass(frozen=True)
class CodecademyCourse:
    title: str
    course_type: str
    level: str
    duration: str


@dataclass(frozen=True)
class CodecademySearchResult:
    query: str
    courses: list[CodecademyCourse]


# Searches Codecademy for courses matching the given query and returns up to max_results
# courses with title, type, skill level, and estimated duration.
def search_codecademy_courses(
    page: Page,
    request: CodecademySearchRequest,
) -> CodecademySearchResult:
    query = request.query
    max_results = request.max_results

    print(f"  Query: {query}  Max results: {max_results}\n")

    results: list[CodecademyCourse] = []

    try:
        # ── Navigate ──────────────────────────────────────────────────
        print("Loading Codecademy search results...")
        search_url = "https://www.codecademy.com/search?query=" + query.replace(" ", "+")
        checkpoint(f"Navigate to {search_url}")
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(8000)
        print(f"  Loaded: {page.url}")

        # ── Extract courses ───────────────────────────────────────────
        print(f"Extracting up to {max_results} courses...")

        body_text = page.evaluate("document.body.innerText") or ""
        lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        TYPE_MARKERS = {"Course", "Skill path", "Career path", "Certification path"}
        FILTER_KEYWORDS = {"Level", "Beginner", "Intermediate", "Advanced", "Price",
                           "Free", "Paid", "Type", "Average time to complete", "All",
                           "Less than 5 hours", "5-10 hours", "10-20 hours",
                           "20-60 hours", "60+ hours", "View plans", "Clear filters",
                           "Filters", "Most relevant"}

        i = 0
        while i < len(lines) and len(results) < max_results:
            if lines[i] in TYPE_MARKERS and i + 1 < len(lines):
                title = lines[i + 1]
                if title in TYPE_MARKERS or title in FILTER_KEYWORDS:
                    i += 1
                    continue

                course_type = lines[i]
                level = "N/A"
                duration = "N/A"

                for k in range(i + 2, min(i + 12, len(lines))):
                    line = lines[k]
                    if line in TYPE_MARKERS:
                        break
                    if "Beginner" in line and "." not in line:
                        level = "Beginner"
                    elif "Intermediate" in line and "." not in line:
                        level = "Intermediate"
                    elif "Advanced" in line and "." not in line:
                        level = "Advanced"
                    elif re.match(r"^(<\s*\d+|\d+)\s+hours?$", line) or line == "< 1 hour":
                        duration = line

                results.append(CodecademyCourse(
                    title=title,
                    course_type=course_type,
                    level=level,
                    duration=duration,
                ))

            i += 1

        # ── Print results ─────────────────────────────────────────────
        print(f"\nFound {len(results)} courses:\n")
        for i, course in enumerate(results, 1):
            print(f"  {i}. {course.title} ({course.course_type})")
            print(f"     Level: {course.level}  Duration: {course.duration}")
            print()

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return CodecademySearchResult(
        query=query,
        courses=results,
    )


def test_search_codecademy_courses() -> None:
    request = CodecademySearchRequest(
        query="Python",
        max_results=5,
    )

    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=False,
            viewport=None,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_codecademy_courses(page, request)
            assert result.query == request.query
            assert len(result.courses) <= request.max_results
            print(f"\nTotal courses found: {len(result.courses)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_codecademy_courses)
