"""
Playwright script (Python) — Avvo.com Lawyer Search
Specialty: immigration
Location: Los Angeles, CA
Max results: 5

Uses the user's Chrome profile for persistent login state.
"""

import re
import os
from urllib.parse import quote_plus
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class AvvoSearchRequest:
    specialty: str
    location: str
    max_results: int


@dataclass(frozen=True)
class AvvoLawyer:
    name: str
    rating: str
    years_experience: str
    num_reviews: str


@dataclass(frozen=True)
class AvvoSearchResult:
    specialty: str
    location: str
    lawyers: list[AvvoLawyer]


# Searches Avvo for lawyers matching the given specialty and location,
# then returns up to max_results lawyers with name, rating, years of experience, and reviews.
def search_avvo_lawyers(
    page: Page,
    request: AvvoSearchRequest,
) -> AvvoSearchResult:
    specialty = request.specialty
    location = request.location
    max_results = request.max_results

    print(f"  Specialty: {specialty}")
    print(f"  Location: {location}")
    print(f"  Max results: {max_results}\n")

    results: list[AvvoLawyer] = []

    try:
        # ── Navigate to search results ────────────────────────────────────
        search_url = f"https://www.avvo.com/search/lawyer_search?q={quote_plus(specialty)}&loc={quote_plus(location)}"
        print(f"Loading {search_url}...")
        checkpoint(f"Navigate to {search_url}")
        page.goto(search_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)
        print(f"  Loaded: {page.url}")

        # ── Extract lawyers ───────────────────────────────────────────────
        print(f"Extracting up to {max_results} lawyers...")

        body_text = page.evaluate("document.body.innerText") or ""
        lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        i = 0
        while i < len(lines) and len(results) < max_results:
            line = lines[i]

            if re.match(r"^\d+\.\d+$", line) and i + 1 < len(lines) and "review" in lines[i + 1].lower():
                rating = line
                reviews_text = lines[i + 1]
                reviews_m = re.search(r"(\d+)\s*reviews?", reviews_text)
                num_reviews = reviews_m.group(1) if reviews_m else "N/A"

                name = "N/A"
                for k in range(max(0, i - 3), i):
                    candidate = lines[k]
                    if (re.match(r"^[A-Z][a-z]", candidate)
                        and len(candidate.split()) >= 2
                        and len(candidate) < 50
                        and "PRO" not in candidate
                        and "SPONSORED" not in candidate
                        and "Save" not in candidate):
                        name = candidate

                years_exp = "N/A"
                for k in range(i, min(i + 8, len(lines))):
                    m = re.search(r"Licensed for (\d+) years?", lines[k])
                    if m:
                        years_exp = m.group(1) + " years"
                        break

                if name != "N/A":
                    results.append(AvvoLawyer(
                        name=name,
                        rating=rating,
                        years_experience=years_exp,
                        num_reviews=num_reviews,
                    ))

            i += 1

        # ── Print results ─────────────────────────────────────────────────
        print(f"\nFound {len(results)} {specialty} lawyers in {location}:\n")
        for i, lawyer in enumerate(results, 1):
            print(f"  {i}. {lawyer.name}")
            print(f"     Rating: {lawyer.rating}  Reviews: {lawyer.num_reviews}  Experience: {lawyer.years_experience}")
            print()

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return AvvoSearchResult(
        specialty=specialty,
        location=location,
        lawyers=results,
    )


def test_search_avvo_lawyers() -> None:
    request = AvvoSearchRequest(
        specialty="immigration",
        location="Los Angeles, CA",
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
            result = search_avvo_lawyers(page, request)
            assert result.specialty == request.specialty
            assert result.location == request.location
            assert len(result.lawyers) <= request.max_results
            print(f"\nTotal lawyers found: {len(result.lawyers)}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_avvo_lawyers)
