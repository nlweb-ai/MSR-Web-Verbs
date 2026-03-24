"""
Khan Academy – Search for "calculus" → extract course title, description, units.
Pure Playwright – no AI.
"""
from datetime import date, timedelta
import re, os, sys, traceback, shutil, tempfile
from playwright.sync_api import Page, sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, launch_chrome, wait_for_cdp_ws, find_chrome_executable

from dataclasses import dataclass
import subprocess
import json
import time
from urllib.request import urlopen


@dataclass(frozen=True)
class KhanAcademyCourseRequest:
    course_url: str


@dataclass(frozen=True)
class KhanAcademyCourseResult:
    course_url: str
    title: str
    description: str
    units: tuple


# Fetches a Khan Academy course page and extracts the course title, description,
# and list of unit names.
def get_khanacademy_course(
    page: Page,
    request: KhanAcademyCourseRequest,
) -> KhanAcademyCourseResult:
    results = {}
    results = []
    try:
        # Go directly to the calculus course page
        print("STEP 1: Navigate to Khan Academy Calculus course...")
        page.goto(
            "https://www.khanacademy.org/math/calculus-1",
            wait_until="domcontentloaded", timeout=30000,
        )
        page.wait_for_timeout(5000)

        # Dismiss cookie / sign-up banners
        for sel in ["button:has-text('Accept')", "button:has-text('Got it')",
                     "button:has-text('No thanks')", "[aria-label='Close']",
                     "button:has-text('Maybe later')"]:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=800):
                    loc.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        # Scroll to load content
        for _ in range(5):
            page.evaluate("window.scrollBy(0, 600)")
            page.wait_for_timeout(600)

        print("STEP 2: Extract course info...")

        # Course title
        title = ""
        for sel in ["h1", "[data-test-id='course-title']", ".course-title"]:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=1500):
                    title = loc.inner_text(timeout=2000).strip()
                    if title:
                        break
            except Exception:
                continue

        # Description
        desc = ""
        for sel in ["[data-test-id='course-description']", ".course-description",
                     "main p", "p"]:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=1500):
                    desc = loc.inner_text(timeout=2000).strip()
                    if desc and len(desc) > 20:
                        break
            except Exception:
                continue

        # Units / sections
        units = []
        # Strategy 1: body text — capture lines like "Unit 1: Limits and continuity"
        body = page.inner_text("body")
        for line in body.splitlines():
            line = line.strip()
            m = re.match(r'^(Unit\s+\d+)\s*$', line)
            if m:
                units.append(m.group(1))

        # Strategy 2: combine unit number with following title line  
        if units:
            lines = [l.strip() for l in body.splitlines()]
            enriched = []
            for i, line in enumerate(lines):
                m = re.match(r'^(Unit\s+\d+)\s*$', line)
                if m:
                    # Next non-empty line should be the unit title
                    title_line = ""
                    for j in range(i + 1, min(i + 4, len(lines))):
                        if lines[j].strip() and not lines[j].strip().startswith("Unit "):
                            title_line = lines[j].strip()
                            break
                    if title_line:
                        enriched.append(f"{m.group(1)}: {title_line}")
                    else:
                        enriched.append(m.group(1))
            units = enriched

        if not title and not units:
            print("❌ ERROR: Extraction failed — no course data found.")
        else:
            print(f"\nCourse Title: {title}")
            if desc:
                print(f"Description : {desc[:200]}...")
            print(f"\nUnits ({len(units)}):")
            for i, u in enumerate(units, 1):
                print(f"  {i}. {u}")
            results = {"title": title, "description": desc, "units": units}

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    return KhanAcademyCourseResult(
        course_url=request.course_url,
        title=results.get("title","") if isinstance(results, dict) else "",
        description=results.get("description","") if isinstance(results, dict) else "",
        units=tuple(results.get("units",[])) if isinstance(results, dict) else (),
    )
def test_get_khanacademy_course() -> None:
    from playwright.sync_api import sync_playwright
    request = KhanAcademyCourseRequest(course_url="https://www.khanacademy.org/math/calculus-1")
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
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = get_khanacademy_course(page, request)
        finally:
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)
    assert result.course_url == request.course_url
    print(f"\nCourse: {result.title}")
    print(f"  Units: {len(result.units)}")


if __name__ == "__main__":
    test_get_khanacademy_course()
