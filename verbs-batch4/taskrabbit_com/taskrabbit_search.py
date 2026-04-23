import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class TaskRabbitSearchRequest:
    service_type: str = "furniture assembly"
    location: str = "San Francisco, CA"
    max_results: int = 5

@dataclass(frozen=True)
class TaskRabbitTasker:
    name: str = ""
    tasks_completed: str = ""
    rating: str = ""
    hourly_rate: str = ""

@dataclass(frozen=True)
class TaskRabbitSearchResult:
    taskers: list = None  # list[TaskRabbitTasker]

# Search TaskRabbit for taskers offering a service in a given location
# and extract name, tasks completed, rating, and hourly rate.
def taskrabbit_search(page: Page, request: TaskRabbitSearchRequest) -> TaskRabbitSearchResult:
    service_type = request.service_type
    location = request.location
    max_results = request.max_results
    print(f"  Service: {service_type}")
    print(f"  Location: {location}")
    print(f"  Max results: {max_results}\n")

    # Service ID 2030 = Furniture Assembly
    book_url = "https://www.taskrabbit.com/book/2030/details?form_referrer=services_page"
    print(f"Loading booking page...")
    checkpoint("Navigate to TaskRabbit booking flow")
    page.goto(book_url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    print(f"  Loaded: {page.url}")

    # Enter location
    print(f"Entering location: {location}...")
    checkpoint("Enter location in booking form")
    loc_input = page.locator('input#location, input[name="location"]').first
    loc_input.click()
    page.wait_for_timeout(500)
    loc_input.fill(location)
    page.wait_for_timeout(2000)

    # Select first autocomplete suggestion
    suggestions = page.locator('[class*="suggestion"], [role="listbox"] li, [role="option"]')
    if suggestions.count() > 0:
        suggestions.first.click()
        page.wait_for_timeout(1000)

    # Click Continue
    page.locator('button:has-text("Continue")').last.click()
    page.wait_for_timeout(2000)
    print("  Location set")

    # Select item type
    print("Selecting item type...")
    checkpoint("Select item type in booking flow")
    try:
        page.locator('text="Other furniture items (non-IKEA)"').first.click()
        page.wait_for_timeout(1000)
        page.locator('button:has-text("Continue")').last.click()
        page.wait_for_timeout(2000)
        print("  Item type selected")
    except Exception:
        print("  Item type step skipped")

    # Select task size
    print("Selecting task size...")
    try:
        page.locator('text="Small - Est. 1 hr"').first.click()
        page.wait_for_timeout(1000)
    except Exception:
        print("  Task size step skipped")

    # Fill description and continue
    try:
        desc = page.locator('textarea').first
        if desc.is_visible(timeout=2000):
            desc.fill("Need help assembling furniture")
            page.wait_for_timeout(500)
    except Exception:
        pass

    # Click Continue until we reach recommendations
    checkpoint("Navigate through booking steps to recommendations")
    for attempt in range(3):
        try:
            cont = page.locator('button:has-text("Continue")')
            if cont.count() > 0:
                cont.last.click()
                page.wait_for_timeout(3000)
                if "recommendations" in page.url:
                    break
        except Exception:
            break

    # If still not on recommendations, try direct navigation
    if "recommendations" not in page.url:
        print("  Navigating directly to recommendations...")
        rec_url = page.url.replace("/details", "/recommendations")
        page.goto(rec_url, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

    print(f"  Recommendations page: {page.url}")

    results = []

    # Extract taskers from recommendations page via body text parsing
    checkpoint("Extract tasker listings from recommendations")
    page.wait_for_timeout(3000)
    body = page.evaluate("document.body.innerText") or ""

    lines = body.split("\n")
    i = 0
    while i < len(lines) and len(results) < max_results:
        line = lines[i].strip()
        name_m = re.match(r'^([A-Z][a-z]+ [A-Z]\.)$', line)
        if name_m and "View" not in line:
            name = name_m.group(1)
            hourly_rate = "N/A"
            rating = "N/A"
            tasks = "N/A"

            for j in range(i + 1, min(i + 10, len(lines))):
                jline = lines[j].strip()
                if not jline:
                    continue
                rate_m = re.search(r'\$(\d+(?:\.\d+)?)/hr', jline)
                if rate_m and hourly_rate == "N/A":
                    hourly_rate = f"${rate_m.group(1)}/hr"
                rating_m = re.search(r'(\d+\.\d+)\s*\((\d+)\s*reviews?\)', jline)
                if rating_m and rating == "N/A":
                    rating = rating_m.group(1)
                tasks_m = re.search(r'(\d+(?:,\d+)?)\s+(?:Furniture|Assembly|tasks?)', jline, re.IGNORECASE)
                if tasks_m and tasks == "N/A":
                    tasks = tasks_m.group(1)
                if re.match(r'^[A-Z][a-z]+ [A-Z]\.$', jline) and jline != name:
                    break

            results.append(TaskRabbitTasker(
                name=name,
                hourly_rate=hourly_rate,
                rating=rating,
                tasks_completed=tasks,
            ))
        i += 1

    print("=" * 60)
    print(f"TaskRabbit - Taskers for \"{service_type}\" in \"{location}\"")
    print("=" * 60)
    for idx, t in enumerate(results, 1):
        print(f"\n{idx}. {t.name}")
        print(f"   Rate: {t.hourly_rate}")
        print(f"   Rating: {t.rating}")
        print(f"   Tasks completed: {t.tasks_completed}")

    print(f"\nFound {len(results)} taskers")

    return TaskRabbitSearchResult(taskers=results)

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = taskrabbit_search(page, TaskRabbitSearchRequest())
        print(f"\nReturned {len(result.taskers or [])} taskers")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
