import re
import os
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


VERSION_RE = re.compile(r'^\u2022 ([\d.]+) \u2022')
DOWNLOADS_RE = re.compile(r'^[\d,]+$')


@dataclass(frozen=True)
class NpmjsSearchRequest:
    query: str = "state management"
    max_results: int = 5


@dataclass(frozen=True)
class NpmPackageInfo:
    name: str = ""
    description: str = ""
    version: str = ""
    downloads: str = ""


@dataclass(frozen=True)
class NpmjsSearchResult:
    packages: list = None


# Search for npm packages by query on npmjs.com and extract package name,
# description, version, and weekly downloads for up to max_results packages.
def npmjs_search(page: Page, request: NpmjsSearchRequest) -> NpmjsSearchResult:
    query = request.query
    max_results = request.max_results
    print(f"  Query: {query}\n")

    results = []

    url = f"https://www.npmjs.com/search?q={quote_plus(query)}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to {url}")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Parse packages - each package ends with a downloads count
    i = 0
    # Skip to 'Search results'
    while i < len(text_lines):
        if "packages found" in text_lines[i]:
            i += 1
            break
        i += 1

    # Skip 'Sort by' line
    if i < len(text_lines) and text_lines[i].startswith('Sort'):
        i += 1

    current_name = None
    current_desc = None
    current_version = None

    while i < len(text_lines) and len(results) < max_results:
        line = text_lines[i]

        # Downloads count (end of a package entry)
        if DOWNLOADS_RE.match(line) and current_name:
            downloads = line
            results.append(NpmPackageInfo(
                name=current_name,
                description=current_desc or "N/A",
                version=current_version or "N/A",
                downloads=downloads,
            ))
            current_name = None
            current_desc = None
            current_version = None
            i += 1
            continue

        # Version line
        vm = VERSION_RE.match(line)
        if vm:
            current_version = vm.group(1)
            i += 1
            # Skip duplicate version line
            if i < len(text_lines) and text_lines[i].startswith('published'):
                i += 1
            continue

        # Package name (appears right after previous downloads or at start)
        if current_name is None:
            current_name = line
            current_desc = text_lines[i + 1] if i + 1 < len(text_lines) else None

        i += 1

    print("=" * 60)
    print(f"npm Search: {query}")
    print("=" * 60)
    for idx, r in enumerate(results, 1):
        print(f"\n{idx}. {r.name} (v{r.version})")
        print(f"   {r.description}")
        print(f"   Weekly downloads: {r.downloads}")

    print(f"\nFound {len(results)} packages")

    return NpmjsSearchResult(packages=results)


def test_func():
    import subprocess, time
    subprocess.call("taskkill /f /im chrome.exe", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    chrome_user_data = os.path.join(
        os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default"
    )
    print(f"Launching Chrome with profile: {chrome_user_data}")
    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            chrome_user_data,
            channel="chrome",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )
        print("Chrome launched successfully")
        page = context.pages[0] if context.pages else context.new_page()
        result = npmjs_search(page, NpmjsSearchRequest())
        for pkg in (result.packages or []):
            print(f"  {pkg.name} v{pkg.version} - {pkg.downloads}")
        context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)