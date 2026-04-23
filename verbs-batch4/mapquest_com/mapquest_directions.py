import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class MapquestDirectionsRequest:
    from_location: str = "Times Square, New York, NY"
    to_location: str = "Central Park, New York, NY"

@dataclass(frozen=True)
class DirectionStep:
    instruction: str = ""
    distance: str = ""

@dataclass(frozen=True)
class MapquestDirectionsResult:
    from_location: str = ""
    to_location: str = ""
    total_distance: str = ""
    estimated_time: str = ""
    steps: list = None  # list[DirectionStep]

# Get driving directions on MapQuest from point A to point B and extract
# total distance, estimated time, and step-by-step directions.
def mapquest_directions(page: Page, request: MapquestDirectionsRequest) -> MapquestDirectionsResult:
    from_loc = request.from_location
    to_loc = request.to_location
    print(f"  From: {from_loc}")
    print(f"  To:   {to_loc}\n")

    # Navigate to directions page
    url = "https://www.mapquest.com/directions"
    print(f"Loading {url}...")
    checkpoint("Navigate to MapQuest")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    print(f"  Loaded: {page.url}")

    # Fill "from" field and select first autocomplete suggestion
    a_input = page.locator('input[name="location-A"]')
    a_input.click()
    a_input.fill(from_loc)
    page.wait_for_timeout(2000)
    suggestions_a = page.locator('[data-suggestion="true"]')
    if suggestions_a.count() > 0:
        chosen = suggestions_a.first.inner_text(timeout=2000).strip()
        print(f"  From suggestion: {chosen[:80]}")
        suggestions_a.first.click()
    else:
        page.keyboard.press("Enter")
    page.wait_for_timeout(2000)

    # Fill "to" field and select first autocomplete suggestion
    b_input = page.locator('input[name="location-B"]')
    b_input.click(force=True)
    page.wait_for_timeout(500)
    b_input.fill(to_loc)
    page.wait_for_timeout(2000)
    suggestions_b = page.locator('[data-suggestion="true"]')
    if suggestions_b.count() > 0:
        chosen = suggestions_b.first.inner_text(timeout=2000).strip()
        print(f"  To suggestion: {chosen[:80]}")
        suggestions_b.first.click()
    else:
        page.keyboard.press("Enter")
    page.wait_for_timeout(3000)

    # Extract summary (total distance + estimated time) from route overview
    total_distance = "N/A"
    estimated_time = "N/A"
    body_text = page.inner_text("body", timeout=5000)

    # Summary format: "3 hr 27 min" and "210.54 miles"
    time_match = re.search(
        r'(\d+\s*hr?\s+\d+\s*min|\d+\s*min)',
        body_text,
        re.IGNORECASE,
    )
    if time_match:
        estimated_time = time_match.group(0).strip()

    dist_match = re.search(r'(\d+[\d,.]*)\s*miles?\b', body_text, re.IGNORECASE)
    if dist_match:
        total_distance = dist_match.group(0).strip()

    # Click "View Directions" to get step-by-step
    view_btn = page.locator('[data-testid="get-directions"]')
    if view_btn.count() > 0:
        print("  Clicking 'View Directions'...")
        view_btn.first.click()
        page.wait_for_timeout(10000)
        print(f"  URL after click: {page.url}")
    else:
        print("  No 'View Directions' button found, trying alternate approach...")
        # Try clicking any remaining Get Directions button
        alt_btn = page.locator('button:has-text("Get Directions")')
        if alt_btn.count() > 0:
            alt_btn.first.click()
            page.wait_for_timeout(10000)

    # Re-read body text after navigation to directions list
    body_text = page.inner_text("body", timeout=5000)
    print(f"  Body length after View: {len(body_text)}")

    # Re-extract summary from the directions list page if needed
    if total_distance == "N/A":
        # Format: "3 hr 27 min(210.54 miles)"
        paren_dist = re.search(r'\((\d+[\d,.]*)\s*miles?\)', body_text, re.IGNORECASE)
        if paren_dist:
            total_distance = paren_dist.group(1).strip() + " miles"
        else:
            dist_match2 = re.search(r'(\d+[\d,.]*)\s*miles?\b', body_text, re.IGNORECASE)
            if dist_match2:
                total_distance = dist_match2.group(0).strip()

    if estimated_time == "N/A":
        time_match2 = re.search(
            r'(\d+\s*hr?\s+\d+\s*min|\d+\s*min)',
            body_text,
            re.IGNORECASE,
        )
        if time_match2:
            estimated_time = time_match2.group(0).strip()

    # Extract step-by-step from maneuver elements
    # Each has format: "Turn left onto Madison Ave.\n\nGo for 0.4 mi."
    steps = []
    step_locators = page.locator('[data-testid*="maneuver"]')
    step_count = step_locators.count()
    print(f"  Found {step_count} maneuver elements")

    for i in range(step_count):
        try:
            step_text = step_locators.nth(i).inner_text(timeout=3000).strip()
            if not step_text or len(step_text) < 3:
                continue

            lines = [l.strip() for l in step_text.split("\n") if l.strip()]
            instruction = ""
            distance = ""

            for line in lines:
                # "Go for 0.4 mi." or "Go for 518 ft."
                go_match = re.match(r'Go for\s+(.+)', line, re.IGNORECASE)
                if go_match:
                    distance = go_match.group(1).rstrip(".")
                    continue
                if not instruction and len(line) > 3:
                    instruction = line

            if instruction:
                steps.append(DirectionStep(instruction=instruction, distance=distance))
        except Exception:
            continue

    # If maneuver selectors didn't work, try text-based fallback
    if not steps:
        print("  Maneuver selectors missed, trying text-based extraction...")
        body_text = page.inner_text("body", timeout=5000)

        # Re-extract summary from directions list page
        time_match2 = re.search(
            r'(\d+\s*hr?\s+\d+\s*min|\d+\s*min)',
            body_text,
            re.IGNORECASE,
        )
        if time_match2:
            estimated_time = time_match2.group(0).strip()

        dist_match2 = re.search(r'\((\d+[\d,.]*)\s*miles?\)', body_text, re.IGNORECASE)
        if dist_match2:
            total_distance = dist_match2.group(1).strip() + " miles"

        direction_keywords = re.compile(
            r'(Turn\s+(left|right)|Head\s+\w+|Merge|Keep\s+(left|right)|Take\s+|'
            r'Continue|Go\s+straight|Slight\s+(left|right)|'
            r'Exit\s+|Make\s+a\s+U-turn)',
            re.IGNORECASE,
        )
        text_lines = [l.strip() for l in body_text.split("\n") if l.strip()]
        i = 0
        while i < len(text_lines):
            line = text_lines[i]
            if direction_keywords.search(line):
                instruction = line
                distance = ""
                # Check next line for "Go for ..." distance
                if i + 1 < len(text_lines):
                    next_line = text_lines[i + 1]
                    go_match = re.match(r'Go for\s+(.+)', next_line, re.IGNORECASE)
                    if go_match:
                        distance = go_match.group(1).rstrip(".")
                        i += 1
                steps.append(DirectionStep(instruction=instruction, distance=distance))
            i += 1

    print("=" * 60)
    print(f"MapQuest Directions: {from_loc} → {to_loc}")
    print("=" * 60)
    print(f"  Total Distance: {total_distance}")
    print(f"  Estimated Time: {estimated_time}")
    print(f"\n  Steps ({len(steps)}):")
    for idx, s in enumerate(steps, 1):
        dist_info = f" ({s.distance})" if s.distance else ""
        print(f"    {idx}. {s.instruction}{dist_info}")

    print(f"\nFound {len(steps)} direction steps")

    return MapquestDirectionsResult(
        from_location=from_loc,
        to_location=to_loc,
        total_distance=total_distance,
        estimated_time=estimated_time,
        steps=steps,
    )

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = mapquest_directions(page, MapquestDirectionsRequest())
        print(f"\nReturned {len(result.steps or [])} direction steps")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
