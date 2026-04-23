"""
Bundlephobia – Look up npm package bundle size information

Uses CDP-launched Chrome to avoid bot detection.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class BundlephobiaSearchRequest:
    package_name: str = "react"


@dataclass
class BundlephobiaItem:
    package_name: str = ""
    version: str = ""
    minified_size: str = ""
    gzipped_size: str = ""
    download_time_3g: str = ""
    download_time_4g: str = ""
    num_dependencies: str = ""
    tree_shakeable: str = ""


@dataclass
class BundlephobiaSearchResult:
    items: List[BundlephobiaItem] = field(default_factory=list)


# Look up npm package bundle size information on Bundlephobia.
def bundlephobia_search(page: Page, request: BundlephobiaSearchRequest) -> BundlephobiaSearchResult:
    """Look up npm package bundle size on Bundlephobia."""
    print(f"  Package: {request.package_name}\n")

    url = f"https://bundlephobia.com/package/{request.package_name}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Bundlephobia package page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    result = BundlephobiaSearchResult()

    checkpoint("Extract bundle size information")
    js_code = """() => {
        const getName = () => {
            const el = document.querySelector('h1, [class*="package-name"], [class*="PackageName"]');
            return el ? el.textContent.trim() : '';
        };
        const getVersion = () => {
            const el = document.querySelector('[class*="version"], [class*="Version"]');
            return el ? el.textContent.trim().replace(/^v/, '') : '';
        };
        const getStatByLabel = (label) => {
            const allEls = document.querySelectorAll('[class*="stat"], [class*="Stat"], div, p, span');
            for (const el of allEls) {
                if (el.textContent.toLowerCase().includes(label.toLowerCase())) {
                    const valueEl = el.querySelector('[class*="value"], [class*="Value"], strong, b, span');
                    if (valueEl && valueEl.textContent.trim() !== el.textContent.trim()) {
                        return valueEl.textContent.trim();
                    }
                    const text = el.textContent.trim();
                    const match = text.match(/[\\d.]+\\s*[kKmMgG]?[bB]/);
                    if (match) return match[0];
                }
            }
            return '';
        };
        const getTreeShakeable = () => {
            const body = document.body.textContent.toLowerCase();
            if (body.includes('tree-shakeable') || body.includes('tree shakeable')) return 'Yes';
            if (body.includes('not tree-shakeable') || body.includes('cannot be tree')) return 'No';
            return '';
        };
        const getDeps = () => {
            const body = document.body.textContent;
            const match = body.match(/(\\d+)\\s*dependenc/i);
            return match ? match[1] : '';
        };
        return [{
            package_name: getName(),
            version: getVersion(),
            minified_size: getStatByLabel('minified'),
            gzipped_size: getStatByLabel('gzip'),
            download_time_3g: getStatByLabel('3g'),
            download_time_4g: getStatByLabel('4g'),
            num_dependencies: getDeps(),
            tree_shakeable: getTreeShakeable()
        }];
    }"""
    items_data = page.evaluate(js_code)

    for d in items_data:
        item = BundlephobiaItem()
        item.package_name = d.get("package_name", "") or request.package_name
        item.version = d.get("version", "")
        item.minified_size = d.get("minified_size", "")
        item.gzipped_size = d.get("gzipped_size", "")
        item.download_time_3g = d.get("download_time_3g", "")
        item.download_time_4g = d.get("download_time_4g", "")
        item.num_dependencies = d.get("num_dependencies", "")
        item.tree_shakeable = d.get("tree_shakeable", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Package {i}:")
        print(f"    Name:           {item.package_name}")
        print(f"    Version:        {item.version}")
        print(f"    Minified:       {item.minified_size}")
        print(f"    Gzipped:        {item.gzipped_size}")
        print(f"    3G Download:    {item.download_time_3g}")
        print(f"    4G Download:    {item.download_time_4g}")
        print(f"    Dependencies:   {item.num_dependencies}")
        print(f"    Tree Shakeable: {item.tree_shakeable}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("bundlephobia")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = BundlephobiaSearchRequest()
            result = bundlephobia_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} packages")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
