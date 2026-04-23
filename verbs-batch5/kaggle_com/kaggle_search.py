"""
Auto-generated Playwright script (Python)
kaggle.com – Dataset Search
Query: climate change

Generated on: 2026-04-18T01:26:48.141Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil, urllib.parse
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class KaggleRequest:
    search_query: str = "climate change"
    max_results: int = 5


@dataclass(frozen=True)
class KaggleDataset:
    title: str = ""
    author: str = ""
    file_size: str = ""
    downloads: str = ""
    usability_rating: str = ""


@dataclass(frozen=True)
class KaggleResult:
    datasets: list = None  # list[KaggleDataset]


def kaggle_search(page: Page, request: KaggleRequest) -> KaggleResult:
    """Search Kaggle for datasets."""
    query = request.search_query
    max_results = request.max_results
    print(f"  Query: {query}")
    print(f"  Max results: {max_results}\n")

    # ── Navigate to search ────────────────────────────────────────────
    url = f"https://www.kaggle.com/datasets?search={urllib.parse.quote_plus(query)}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Kaggle datasets search")
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(5000)

    # ── Extract dataset cards ─────────────────────────────────────────
    datasets = page.evaluate(r"""(maxResults) => {
        const items = document.querySelectorAll('li.MuiListItem-root');
        const results = [];
        for (const item of items) {
            if (results.length >= maxResults) break;
            const text = item.innerText;
            const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
            if (lines.length < 3) continue;
            const title = lines[0];
            if (title === 'more_horiz' || title.length < 3) continue;
            const authorLine = lines.find(l => l.includes('Updated'));
            const author = authorLine ? authorLine.split('\u00b7')[0].trim() : '';
            const metaLine = lines.find(l => l.includes('Usability'));
            if (!metaLine) continue;
            const usabilityMatch = metaLine.match(/Usability\s+([\d.]+)/);
            const usability = usabilityMatch ? usabilityMatch[1] : '';
            const sizeMatch = metaLine.match(/\u00b7\s*([\d.,]+\s*(?:kB|MB|GB|TB|bytes))\s*\u00b7/);
            const fileSize = sizeMatch ? sizeMatch[1] : '';
            const dlMatch = metaLine.match(/([\d.,]+[KMB]?)\s*downloads/);
            const downloads = dlMatch ? dlMatch[1] : '';
            results.push({ title, author, file_size: fileSize, downloads, usability_rating: usability });
        }
        return results;
    }""", max_results)

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f'Kaggle - "{query}" Datasets')
    print("=" * 60)
    for idx, d in enumerate(datasets, 1):
        print(f"\n{idx}. {d['title']}")
        print(f"   Author: {d['author']} | Size: {d['file_size']} | Downloads: {d['downloads']}")
        print(f"   Usability: {d['usability_rating']}")

    print(f"\nFound {len(datasets)} datasets")
    return KaggleResult(
        datasets=[KaggleDataset(**d) for d in datasets]
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("kaggle_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = kaggle_search(page, KaggleRequest())
            print(f"\nReturned {len(result.datasets or [])} datasets")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
