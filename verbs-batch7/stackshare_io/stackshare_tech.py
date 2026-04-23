"""
Auto-generated Playwright script (Python)
StackShare – Technology Lookup

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil, re
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class TechRequest:
    tech_slug: str = "react"


@dataclass
class TechResult:
    tech_name: str = ""
    category: str = ""
    description: str = ""
    stacks_count: str = ""
    followers_count: str = ""
    pros: List[str] = field(default_factory=list)


def stackshare_tech(page: Page, request: TechRequest) -> TechResult:
    """Look up a technology on StackShare."""
    print(f"  Technology: {request.tech_slug}\n")

    url = f"https://stackshare.io/{request.tech_slug}"
    print(f"Loading {url}...")
    checkpoint("Navigate to tech page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = TechResult()

    checkpoint("Extract technology data")
    body = page.evaluate("document.body.innerText")

    # Tech name - first line after "Sign in"
    m = re.search(r'Sign in\nBy\n(.+?)(?:\n|$)', body)
    if m:
        result.tech_name = m.group(1).strip()

    # Category
    m = re.search(r'in\s+(.+?)(?:\n|$)', body)
    if m:
        result.category = m.group(1).strip()

    # Stacks count
    m = re.search(r'Stacks\n([\d.]+k?)', body)
    if m:
        result.stacks_count = m.group(1)

    # Followers count
    m = re.search(r'Followers\n([\d.]+k?)', body)
    if m:
        result.followers_count = m.group(1)

    # Description - "What is X?" section
    m = re.search(r'What is \w+\?\n\n(.+?)(?:\n\n|$)', body, re.DOTALL)
    if m:
        result.description = m.group(1).strip()

    # Top pros
    lines = body.split('\n')
    in_pros = False
    for i, line in enumerate(lines):
        if 'Pros of' in line:
            in_pros = True
            continue
        if in_pros:
            if line.strip() and re.match(r'^\d+$', line.strip()):
                # This is a vote count, next line is the pro
                if i + 1 < len(lines):
                    pro = lines[i + 1].strip()
                    if pro and not pro.startswith('Cons') and len(result.pros) < 5:
                        result.pros.append(pro)
            if 'Cons of' in line:
                break

    print(f"  Name:       {result.tech_name}")
    print(f"  Category:   {result.category}")
    print(f"  Stacks:     {result.stacks_count}")
    print(f"  Followers:  {result.followers_count}")
    print(f"  Description: {result.description[:100]}...")
    print(f"  Top Pros:")
    for p in result.pros:
        print(f"    - {p}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("stackshare")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = TechRequest()
            result = stackshare_tech(page, request)
            print("\n=== DONE ===")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
