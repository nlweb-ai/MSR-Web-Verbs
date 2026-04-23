"""
Playwright script (Python) — BBB.org Business Profile Search
Query: Comcast

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
class BbbSearchRequest:
    query: str


@dataclass(frozen=True)
class BbbProfileResult:
    business_name: str
    bbb_rating: str
    accreditation: str
    customer_review_rating: str
    review_count: str
    total_complaints: str


# Searches BBB.org for a business by name, navigates to its profile,
# and extracts BBB rating, accreditation status, customer review rating, and complaint count.
def search_bbb_profile(
    page: Page,
    request: BbbSearchRequest,
) -> BbbProfileResult:
    query = request.query

    print(f"  Query: {query}\n")

    try:
        # ── Navigate to BBB and search ────────────────────────────────
        print("Searching BBB.org...")
        checkpoint("Navigate to https://www.bbb.org")
        page.goto("https://www.bbb.org")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        try:
            accept_btn = page.locator("button:has-text('Accept All Cookies')")
            if accept_btn.count() > 0:
                checkpoint("Accept cookies")
                accept_btn.first.click()
                page.wait_for_timeout(1000)
        except Exception:
            pass

        checkpoint(f"Fill search query: {query}")
        page.evaluate("""(q) => {
            const input = document.querySelector('input[name="find_text"], input[placeholder*="Find"]');
            if (input) {
                input.value = q;
                input.dispatchEvent(new Event('input', {bubbles: true}));
            }
        }""", query)
        page.wait_for_timeout(500)

        checkpoint("Submit search form")
        page.evaluate("""() => {
            const form = document.querySelector('form[action*="search"]');
            if (form) form.submit();
            else {
                const btn = document.querySelector('button[type="submit"]');
                if (btn) btn.click();
            }
        }""")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(8000)
        print(f"  Search results: {page.url}")

        checkpoint("Click first business profile link")
        profile_link = page.locator("a[href*='/profile/']").first
        profile_link.click(timeout=10000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(8000)
        print(f"  Profile page: {page.url}")

        # ── Extract from MAIN tab ────────────────────────────────────
        body_text = page.evaluate("document.body.innerText") or ""
        lines = [l.strip() for l in body_text.split("\n") if l.strip()]

        business_name = query
        for i, line in enumerate(lines):
            if "BUSINESS PROFILE" in line and i + 2 < len(lines):
                business_name = lines[i + 2]
                break

        bbb_rating = "N/A"
        for i, line in enumerate(lines):
            if line == "BBB Rating" and i + 1 < len(lines):
                bbb_rating = lines[i + 1]
                break

        accredited = "N/A"
        for line in lines:
            if "NOT BBB Accredited" in line or "NOT a BBB Accredited" in line:
                accredited = "Not Accredited"
                break
            elif "BBB Accredited" in line and "NOT" not in line and "Find" not in line and "become" not in line.lower():
                accredited = "Accredited"
                break
        if accredited == "N/A":
            for line in lines:
                if "is NOT a BBB Accredited" in line:
                    accredited = "Not Accredited"
                    break
                elif "is a BBB Accredited" in line:
                    accredited = "Accredited"
                    break

        # ── Navigate to Reviews tab ───────────────────────────────────
        review_rating = "N/A"
        review_count = "N/A"
        try:
            profile_url = page.url.rstrip("/")
            if "/addressId/" in profile_url:
                profile_url = profile_url.split("/addressId/")[0]
            reviews_url = profile_url + "/customer-reviews"
            checkpoint("Navigate to customer reviews tab")
            page.goto(reviews_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(5000)

            review_text = page.evaluate("document.body.innerText") or ""
            review_lines = [l.strip() for l in review_text.split("\n") if l.strip()]

            for i, line in enumerate(review_lines):
                if "Customer Review Ratings" in line:
                    if i + 1 < len(review_lines):
                        m = re.match(r"^(\d+\.\d+)$", review_lines[i + 1])
                        if m:
                            review_rating = m.group(1) + "/5"
                    break

            for line in review_lines:
                m = re.search(r"Average of ([\d,]+) Customer Reviews", line)
                if m:
                    review_count = m.group(1)
                    break
        except Exception:
            pass

        # ── Navigate to Complaints tab ────────────────────────────────
        total_complaints = "N/A"
        try:
            current_url = page.url.split("/customer-reviews")[0].split("#")[0].rstrip("/")
            if "/addressId/" in current_url:
                current_url = current_url.split("/addressId/")[0]
            complaints_url = current_url + "/complaints"
            checkpoint("Navigate to complaints tab")
            page.goto(complaints_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(5000)

            complaint_text = page.evaluate("document.body.innerText") or ""
            for line in complaint_text.split("\n"):
                m = re.search(r"([\d,]+) total complaints", line)
                if m:
                    total_complaints = m.group(1)
                    break
        except Exception:
            pass

        result = BbbProfileResult(
            business_name=business_name,
            bbb_rating=bbb_rating,
            accreditation=accredited,
            customer_review_rating=review_rating,
            review_count=review_count,
            total_complaints=total_complaints,
        )

        # ── Print results ─────────────────────────────────────────────
        print(f"\nBBB Profile for {result.business_name}:\n")
        print(f"  BBB Rating:            {result.bbb_rating}")
        print(f"  Accreditation:         {result.accreditation}")
        print(f"  Customer Review Rating: {result.customer_review_rating}")
        print(f"  Number of Reviews:     {result.review_count}")
        print(f"  Total Complaints:      {result.total_complaints}")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()
        result = BbbProfileResult(
            business_name=query,
            bbb_rating="N/A",
            accreditation="N/A",
            customer_review_rating="N/A",
            review_count="N/A",
            total_complaints="N/A",
        )

    return result


def test_search_bbb_profile() -> None:
    request = BbbSearchRequest(
        query="Comcast",
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
            result = search_bbb_profile(page, request)
            assert result.business_name != "N/A"
            print(f"\nProfile retrieved for: {result.business_name}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_search_bbb_profile)
