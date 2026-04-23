"""
Auto-generated Playwright script (Python)
exercism.org – Python Track Exercises
Track: python

Generated on: 2026-04-18T00:57:43.704Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import os, sys, shutil
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class ExercismRequest:
    track: str = "python"
    max_results: int = 10


@dataclass(frozen=True)
class ExercismExercise:
    exercise_name: str = ""
    difficulty: str = ""
    description: str = ""


@dataclass(frozen=True)
class ExercismResult:
    exercises: list = None  # list[ExercismExercise]


def exercism_exercises(page: Page, request: ExercismRequest) -> ExercismResult:
    """Browse Exercism track exercises."""
    track = request.track
    max_results = request.max_results
    print(f"  Track: {track}")
    print(f"  Max results: {max_results}\n")

    # ── Navigate ──────────────────────────────────────────────────────
    url = f"https://exercism.org/tracks/{track}/exercises"
    print(f"Loading {url}...")
    checkpoint("Navigate to Exercism exercises")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    print(f"  Loaded: {page.url}")

    # ── Extract exercises ─────────────────────────────────────────────
    checkpoint("Extract exercise listings")
    results_data = page.evaluate(r"""(maxResults) => {
        const widgets = document.querySelectorAll('a.c-exercise-widget');
        const results = [];
        for (const w of widgets) {
            if (results.length >= maxResults) break;
            const titleEl = w.querySelector('.--title');
            const typeEl = w.querySelector('.c-exercise-type-tag');
            const blurbEl = w.querySelector('.--blurb');
            if (!titleEl) continue;
            results.push({
                name: titleEl.textContent.trim(),
                difficulty: typeEl ? typeEl.textContent.trim() : '',
                description: blurbEl ? blurbEl.textContent.trim() : ''
            });
        }
        return results;
    }""", max_results)

    exercises = []
    for r in results_data:
        exercises.append(ExercismExercise(
            exercise_name=r.get("name", ""),
            difficulty=r.get("difficulty", ""),
            description=r.get("description", ""),
        ))

    # ── Print results ─────────────────────────────────────────────────
    print("=" * 60)
    print(f'Exercism - {track.title()} Track Exercises')
    print("=" * 60)
    for idx, e in enumerate(exercises, 1):
        print(f"\n{idx}. {e.exercise_name}")
        print(f"   Difficulty: {e.difficulty}")
        print(f"   {e.description}")

    print(f"\nFound {len(exercises)} exercises")
    return ExercismResult(exercises=exercises)


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("exercism_org")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = exercism_exercises(page, ExercismRequest())
            print(f"\nReturned {len(result.exercises or [])} exercises")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
