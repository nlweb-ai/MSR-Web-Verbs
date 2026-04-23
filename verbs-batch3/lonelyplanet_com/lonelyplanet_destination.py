import re
import os
from dataclasses import dataclass
from typing import Optional
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


ATTRACTION_RE = re.compile(r'^ATTRACTION IN (.+)$')


@dataclass(frozen=True)
class LonelyplanetDestinationRequest:
    country: str = "japan"
    destination: str = "tokyo"
    max_attractions: int = 5


@dataclass(frozen=True)
class Attraction:
    name: str
    area: str


@dataclass(frozen=True)
class LonelyplanetDestinationResult:
    destination: str
    overview: Optional[str]
    best_time: Optional[str]
    attractions: tuple[Attraction, ...]


# Navigates to a Lonely Planet destination page by country and city,
# extracts the destination overview, best time to visit, and top attractions
# (up to max_attractions) with names and areas.
def lonelyplanet_destination(page: Page, request: LonelyplanetDestinationRequest) -> LonelyplanetDestinationResult:
    destination = request.destination
    country = request.country
    max_attractions = request.max_attractions
    print(f"  Destination: {destination.title()}")

    url = f"https://www.lonelyplanet.com/{country}/{destination}"
    print(f"Loading {url}...")
    checkpoint("Navigate to page")
    page.goto(url)
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    overview = None
    best_time = None
    attractions = []

    i = 0
    while i < len(text_lines):
        line = text_lines[i]

        if line.lower().startswith('why visit') and i + 1 < len(text_lines):
            overview = text_lines[i + 1]

        if line == "BEST TIME TO VISIT" and i + 1 < len(text_lines):
            best_time = text_lines[i + 1]

        m = ATTRACTION_RE.match(line)
        if m and len(attractions) < max_attractions and i + 1 < len(text_lines):
            area = m.group(1).title()
            name = text_lines[i + 1]
            if name != "DISCOVER":
                attractions.append(Attraction(name=name, area=area))

        i += 1

    dest_title = destination.title()
    print("=" * 60)
    print(f"Lonely Planet: {dest_title} Destination Guide")
    print("=" * 60)
    print(f"\nOverview:")
    print(f"  {overview or 'N/A'}")
    print(f"\nBest Time to Visit:")
    print(f"  {best_time or 'N/A'}")
    print(f"\nTop Attractions:")
    for idx, a in enumerate(attractions, 1):
        print(f"  {idx}. {a.name}")
        print(f"     Area: {a.area}")

    return LonelyplanetDestinationResult(
        destination=dest_title,
        overview=overview,
        best_time=best_time,
        attractions=tuple(attractions),
    )


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    with sync_playwright() as pw:
        user_data_dir = os.path.join(
            os.environ["USERPROFILE"],
            "AppData", "Local", "Google", "Chrome", "User Data", "Default",
        )
        context = pw.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            channel="chrome",
        )
        page = context.pages[0] if context.pages else context.new_page()
        request = LonelyplanetDestinationRequest()
        result = lonelyplanet_destination(page, request)
        print(f"\nResult: {result}")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)