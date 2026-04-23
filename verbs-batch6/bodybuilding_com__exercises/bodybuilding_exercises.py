"""
Auto-generated Playwright script (Python)
Bodybuilding.com – Exercise Database
Muscle: "chest"

Generated on: 2026-04-18T04:58:48.372Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ExerciseRequest:
    muscle: str = "chest"
    max_exercises: int = 5


@dataclass
class Exercise:
    name: str = ""
    muscle_group: str = ""
    equipment: str = ""
    difficulty: str = ""


@dataclass
class ExerciseResult:
    exercises: list = field(default_factory=list)


def bodybuilding_exercises(page: Page, request: ExerciseRequest) -> ExerciseResult:
    """Search Bodybuilding.com exercise database for exercises by muscle group.
    
    NOTE: Bodybuilding.com has shut down its exercise database and now redirects
    all /exercises/ URLs to its supplement shop (shop.bodybuilding.com).
    This script attempts to find exercise content but may return no results.
    """
    print(f"  Muscle: {request.muscle}\n")

    # ── Step 1: Try the exercise database ─────────────────────────────
    url = "https://www.bodybuilding.com/exercises"
    print(f"Loading {url}...")
    checkpoint("Navigate to exercise database")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # Check if redirected to shop
    if "shop.bodybuilding.com" in page.url:
        print("  Exercise database no longer exists (redirects to shop).")
        print("  Trying workouts/articles section...")

        # Try to find any exercise-related articles
        page.goto("https://shop.bodybuilding.com/blogs/workouts", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)

        if "404" in page.title():
            # Try articles section
            page.goto("https://shop.bodybuilding.com/blogs/articles", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)

    # ── Step 2: Extract any exercise content found ────────────────────
    checkpoint("Extract exercise content")
    exercises_data = page.evaluate(r"""(args) => {
        const muscle = args.muscle.toLowerCase();
        const max = args.max;
        const results = [];

        // Look for article/blog links about the target muscle
        const links = document.querySelectorAll('a');
        const seen = new Set();
        for (const a of links) {
            if (results.length >= max) break;
            const text = a.innerText.trim();
            const href = a.href || '';
            if (text.length < 10 || seen.has(text)) continue;
            if (text.toLowerCase().includes(muscle) || href.toLowerCase().includes(muscle)) {
                seen.add(text);
                results.push({
                    name: text.slice(0, 150),
                    muscle_group: muscle,
                    equipment: '',
                    difficulty: '',
                    url: href
                });
            }
        }
        return results;
    }""", {"muscle": request.muscle, "max": request.max_exercises})

    result = ExerciseResult(
        exercises=[Exercise(name=e['name'], muscle_group=e['muscle_group'],
                          equipment=e['equipment'], difficulty=e['difficulty'])
                  for e in exercises_data]
    )

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Bodybuilding.com: {request.muscle} exercises")
    print("=" * 60)
    if not exercises_data:
        print("  No exercise database found.")
        print("  Bodybuilding.com has shut down its exercise finder")
        print("  and now operates as a supplement shop only.")
    else:
        for i, e in enumerate(exercises_data, 1):
            print(f"\n  {i}. {e['name']}")
            if e.get('muscle_group'):
                print(f"     Muscle: {e['muscle_group']}")
            if e.get('equipment'):
                print(f"     Equipment: {e['equipment']}")
            if e.get('difficulty'):
                print(f"     Difficulty: {e['difficulty']}")
            if e.get('url'):
                print(f"     URL: {e['url']}")
    print(f"\n  Total: {len(result.exercises)} exercises")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("bodybuilding_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = bodybuilding_exercises(page, ExerciseRequest())
            print(f"\nReturned {len(result.exercises)} exercises")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
