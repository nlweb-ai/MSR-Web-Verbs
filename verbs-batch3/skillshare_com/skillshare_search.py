"""
Playwright verb — Skillshare Class Search
Search for classes by keyword.
Extract class title, teacher name, duration, and number of students.

URL pattern: https://www.skillshare.com/en/search?query={query}
"""

import re
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


DURATION_RE = re.compile(r"^(\d+h\s*)?\d+m$")
STUDENTS_RE = re.compile(r"^[\d,.]+k?$", re.IGNORECASE)
LEVEL_KEYWORDS = {"Any level", "Beginner", "Intermediate", "Advanced"}


@dataclass(frozen=True)
class SkillshareSearchRequest:
    query: str = "illustration"
    max_results: int = 5


@dataclass(frozen=True)
class SkillshareClass:
    title: str = ""
    teacher: str = ""
    duration: str = ""
    students: str = ""


@dataclass(frozen=True)
class SkillshareSearchResult:
    classes: tuple = ()


# Search for classes on Skillshare by keyword.
# Navigate to the search results page, then parse the body text to extract
# up to max_results classes with title, teacher name, duration, and student count.
def skillshare_search(page: Page, request: SkillshareSearchRequest) -> SkillshareSearchResult:
    print(f"  Query: {request.query}")
    print(f"  Max results: {request.max_results}\n")

    results = []

    search_url = f"https://www.skillshare.com/en/search?query={quote_plus(request.query)}"
    print(f"Loading {search_url}...")

    checkpoint("Navigate to Skillshare search results")
    page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(6000)
    print(f"  Loaded: {page.url}")

    body = page.locator("body").inner_text(timeout=10000)
    lines = [l.strip() for l in body.split("\n") if l.strip()]

    print(f"\nParsing {len(lines)} body lines...")

    # Find "Classes" section start — look for "(N Results)" after "Classes"
    start_idx = 0
    for i, l in enumerate(lines):
        if re.match(r"^\(\d[\d,.]*\s+Results?\)$", l):
            start_idx = i + 1
            print(f"  Classes section starts at line {i}: {l}")
            break

    # Find end of classes section — "Learning Paths" or "Digital Products"
    end_idx = len(lines)
    for i in range(start_idx, len(lines)):
        if lines[i] in ("Learning Paths", "Digital Products", "Shop Digital Products"):
            end_idx = i
            break

    # Parse class blocks using duration line as anchor
    # Pattern: ... teacher → [rating] → [(reviews)] → title → tags... → level → students → duration
    i = start_idx
    while i < end_idx and len(results) < request.max_results:
        if DURATION_RE.match(lines[i]):
            duration = lines[i]

            # Students is right before duration
            students = "N/A"
            if i - 1 >= start_idx and STUDENTS_RE.match(lines[i - 1]):
                students = lines[i - 1]

            # Level is before students
            level_idx = i - 2
            if level_idx >= start_idx and lines[level_idx] in LEVEL_KEYWORDS:
                pass  # valid level
            else:
                level_idx = i - 2  # skip anyway

            # Walk backwards past tags/level to find title
            title = "N/A"
            teacher = "N/A"
            j = level_idx - 1 if level_idx >= start_idx else i - 3

            # Skip tag lines (short, often "+N" or single words like "Procreate")
            while j >= start_idx:
                line = lines[j]
                if re.match(r"^\+\d+$", line):
                    j -= 1
                    continue
                if len(line) <= 25 and not re.match(r"^\d", line) and line not in LEVEL_KEYWORDS:
                    j -= 1
                    continue
                break

            # This should be the title
            if j >= start_idx:
                title = lines[j]
                j -= 1

            # Skip optional review count "(N)" and rating "4.8"
            while j >= start_idx:
                line = lines[j]
                if re.match(r"^\([\d,.k]+\)$", line, re.IGNORECASE):
                    j -= 1
                    continue
                if re.match(r"^\d(\.\d)?$", line):
                    j -= 1
                    continue
                if line == "New":
                    j -= 1
                    continue
                break

            # This should be the teacher
            if j >= start_idx:
                candidate = lines[j]
                if not candidate.startswith("View all") and not candidate.startswith("Learn "):
                    teacher = candidate

            if title != "N/A":
                results.append(SkillshareClass(
                    title=title,
                    teacher=teacher,
                    duration=duration,
                    students=students,
                ))

            i += 1
            continue
        i += 1

    print(f'\nFound {len(results)} classes for "{request.query}":\n')
    for idx, c in enumerate(results, 1):
        print(f"  {idx}. {c.title}")
        print(f"     Teacher: {c.teacher}")
        print(f"     Duration: {c.duration}  Students: {c.students}")
        print()

    return SkillshareSearchResult(classes=tuple(results))


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_user_data = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            chrome_user_data,
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        result = skillshare_search(page, SkillshareSearchRequest())
        print(f"\nTotal classes found: {len(result.classes)}")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
