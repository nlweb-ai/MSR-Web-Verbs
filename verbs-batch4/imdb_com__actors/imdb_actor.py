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
class ImdbActorRequest:
    query: str = "Meryl Streep"
    max_films: int = 5

@dataclass(frozen=True)
class ImdbFilm:
    film_title: str = ""
    year: str = ""
    role: str = ""

@dataclass(frozen=True)
class ImdbActorResult:
    actor_name: str = ""
    birth_date: str = ""
    biography: str = ""
    films: list = None  # list[ImdbFilm]

# Search for an actor on IMDB, click their profile, and extract
# actor name, birth date, biography, and notable filmography.
def imdb_actor(page: Page, request: ImdbActorRequest) -> ImdbActorResult:
    query = request.query
    max_films = request.max_films
    print(f"  Search query: {query}")
    print(f"  Max films: {max_films}\n")

    url = f"https://www.imdb.com/find/?q={quote_plus(query)}&s=nm"
    print(f"Loading {url}...")
    checkpoint("Navigate to IMDB search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    # Click the first search result
    first_result = page.locator(
        'a[href*="/name/nm"],'
        ' .ipc-metadata-list-summary-item a,'
        ' .find-name-result a'
    ).first
    try:
        first_result.click(timeout=5000)
    except Exception:
        print("  Could not click first result, trying fallback selector...")
        page.locator("a.ipc-metadata-list-summary-item__t").first.click(timeout=5000)
    page.wait_for_timeout(8000)
    print(f"  Profile page: {page.url}")

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""

    # --- Extract actor name ---
    actor_name = "N/A"
    name_el = page.locator('h1[data-testid="hero__pageTitle"], h1 span.hero__primary-text, h1')
    try:
        actor_name = name_el.first.inner_text(timeout=3000).strip()
    except Exception:
        # Fallback: first bold/large line in body
        for line in body_text.split("\n"):
            line = line.strip()
            if line and len(line) > 2 and len(line) < 60:
                actor_name = line
                break

    # --- Extract birth date ---
    birth_date = "N/A"
    bd_match = re.search(r'Born\s*[:\-]?\s*([A-Za-z]+ \d{1,2},?\s*\d{4})', body_text)
    if bd_match:
        birth_date = bd_match.group(1).strip()
    else:
        bd_match2 = re.search(r'(\w+ \d{1,2}, \d{4})', body_text)
        if bd_match2:
            birth_date = bd_match2.group(1).strip()

    # --- Extract biography ---
    biography = "N/A"
    bio_el = page.locator(
        '[data-testid="bio-content"] .ipc-html-content-inner-div,'
        ' [data-testid="hero-bio-text"],'
        ' .inline-text-bio'
    )
    try:
        biography = bio_el.first.inner_text(timeout=3000).strip()
        # Truncate long bios
        if len(biography) > 500:
            biography = biography[:497] + "..."
    except Exception:
        bio_match = re.search(r'(?:Biography|Mini Bio).*?\n(.+?)(?:\n\n|\nSee full bio)', body_text, re.DOTALL)
        if bio_match:
            biography = bio_match.group(1).strip()[:500]

    # --- Extract notable films from "Known for" section in body text ---
    films = []

    # Body text pattern in "Known for":
    #   title (e.g. "Mamma Mia!")
    #   rating (e.g. "6.5")
    #   role (e.g. "Donna")
    #   year (e.g. "2008")
    text_lines = [l.strip() for l in body_text.split("\n") if l.strip()]
    known_idx = None
    for idx, line in enumerate(text_lines):
        if line.lower() == "known for":
            known_idx = idx
            break

    if known_idx is not None:
        i = known_idx + 1
        while i < len(text_lines) and len(films) < max_films:
            line = text_lines[i]
            # Stop at "Credits" or other section headers
            if line in ("Credits", "Edit", "Photos", "Personal details"):
                break
            # Check if this looks like a movie title (not a pure number or year)
            if (len(line) > 1 and not re.match(r'^\d+\.?\d*$', line)
                    and not re.match(r'^(19|20)\d{2}$', line)):
                film_title = line
                rating = "N/A"
                role = "N/A"
                year = "N/A"
                # Next lines should be: rating, role, year
                if i + 1 < len(text_lines) and re.match(r'^\d+\.?\d*$', text_lines[i + 1]):
                    rating = text_lines[i + 1]
                if i + 2 < len(text_lines) and not re.match(r'^(19|20)\d{2}$', text_lines[i + 2]):
                    role = text_lines[i + 2]
                if i + 3 < len(text_lines) and re.match(r'^(19|20)\d{2}$', text_lines[i + 3]):
                    year = text_lines[i + 3]
                elif i + 2 < len(text_lines) and re.match(r'^(19|20)\d{2}$', text_lines[i + 2]):
                    year = text_lines[i + 2]
                    role = "N/A"

                films.append(ImdbFilm(film_title=film_title, year=year, role=role))
                i += 4
                continue
            i += 1

    films = films[:max_films]

    print("=" * 60)
    print(f"IMDB - Actor Profile: {actor_name}")
    print("=" * 60)
    print(f"  Name: {actor_name}")
    print(f"  Born: {birth_date}")
    print(f"  Bio:  {biography[:120]}{'...' if len(biography) > 120 else ''}")
    print(f"\n  Notable Films ({len(films)}):")
    for idx, f in enumerate(films, 1):
        print(f"    {idx}. {f.film_title} ({f.year}) — {f.role}")

    print(f"\nFound {len(films)} films")

    return ImdbActorResult(
        actor_name=actor_name,
        birth_date=birth_date,
        biography=biography,
        films=films,
    )

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = imdb_actor(page, ImdbActorRequest())
        print(f"\nReturned {len(result.films or [])} films")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
