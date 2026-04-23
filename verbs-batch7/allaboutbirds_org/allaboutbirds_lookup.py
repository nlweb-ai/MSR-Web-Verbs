"""
Auto-generated Playwright script (Python)
All About Birds – Bird Species Lookup
Bird: "bald eagle"

Uses CDP-launched Chrome to avoid bot detection.
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BirdRequest:
    bird_name: str = "bald eagle"


@dataclass
class BirdResult:
    common_name: str = ""
    scientific_name: str = ""
    size_wingspan: str = ""
    habitat: str = ""
    diet: str = ""
    conservation_status: str = ""


def allaboutbirds_lookup(page: Page, request: BirdRequest) -> BirdResult:
    """Look up a bird species on All About Birds."""
    print(f"  Bird: {request.bird_name}\n")

    # ── Navigate to bird guide page ───────────────────────────────────
    # URL pattern: /guide/Bird_Name/overview (spaces → underscores, no apostrophes)
    slug = request.bird_name.strip().replace(" ", "_").replace("'", "")
    url = f"https://www.allaboutbirds.org/guide/{slug}/overview"
    print(f"Loading {url}...")
    checkpoint("Navigate to All About Birds")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    result = BirdResult()

    # ── Check if page loaded (might redirect to search) ──────────────
    if "/guide/" not in page.url or "overview" not in page.url:
        # Fell through to search — try clicking first result
        try:
            first_link = page.locator('a[href*="/guide/"]').first
            if first_link.is_visible(timeout=2000):
                first_link.click()
                page.wait_for_timeout(3000)
        except Exception:
            print("  Could not find bird page")
            return result

    # ── Common name ───────────────────────────────────────────────────
    checkpoint("Extract bird info")
    try:
        result.common_name = page.locator("h1").first.inner_text().strip()
    except Exception:
        pass

    # ── Scientific name (in the callout div) ──────────────────────────
    try:
        callout = page.locator("div.callout").first
        text = callout.inner_text()
        # Pattern: "Eagles\nBald Eagle\nHaliaeetus leucocephalus\nORDER:..."
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for i, line in enumerate(lines):
            # Scientific name is typically the italic line after the common name
            if "ORDER:" in line:
                break
            # Scientific name has two words, first capitalized
            if re.match(r"^[A-Z][a-z]+ [a-z]+", line) and line != result.common_name:
                result.scientific_name = line
                break
    except Exception:
        pass

    # ── Habitat, Food, Conservation from callout text ─────────────────
    try:
        callout = page.locator("div.callout").first
        text = callout.inner_text()

        # Extract Habitat
        m = re.search(r"Habitat\n(.+?)(?:\n|$)", text)
        if m:
            result.habitat = m.group(1).strip()

        # Extract Food/Diet
        m = re.search(r"Food\n(.+?)(?:\n|$)", text)
        if m:
            result.diet = m.group(1).strip()

        # Extract Conservation
        m = re.search(r"Conservation\n(.+?)(?:\n|$)", text)
        if m:
            result.conservation_status = m.group(1).strip()
    except Exception:
        pass

    # ── Size/Wingspan (on the ID info page) ───────────────────────────
    try:
        id_url = page.url.replace("/overview", "/id")
        page.goto(id_url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        body = page.locator("body").inner_text()
        # Look for size measurements
        m = re.search(r"Length[:\s]+([\d.]+[^\n]+)", body)
        length = m.group(1).strip() if m else ""
        m = re.search(r"Wingspan[:\s]+([\d.]+[^\n]+)", body)
        wingspan = m.group(1).strip() if m else ""
        if length and wingspan:
            result.size_wingspan = f"Length: {length}, Wingspan: {wingspan}"
        elif length:
            result.size_wingspan = f"Length: {length}"
        elif wingspan:
            result.size_wingspan = f"Wingspan: {wingspan}"
    except Exception:
        pass

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"All About Birds: {request.bird_name}")
    print("=" * 60)
    print(f"  Common Name:         {result.common_name}")
    print(f"  Scientific Name:     {result.scientific_name}")
    print(f"  Size/Wingspan:       {result.size_wingspan}")
    print(f"  Habitat:             {result.habitat}")
    print(f"  Diet:                {result.diet}")
    print(f"  Conservation Status: {result.conservation_status}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("allaboutbirds_org")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = allaboutbirds_lookup(page, BirdRequest())
            print(f"\nDone. Found: {result.common_name}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
