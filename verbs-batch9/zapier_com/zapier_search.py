"""Playwright script (Python) — Zapier"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class ZapierRequest:
    query: str = "Google Sheets"
    max_results: int = 5

@dataclass
class ZapItem:
    name: str = ""
    apps: str = ""

@dataclass
class ZapierResult:
    zaps: List[ZapItem] = field(default_factory=list)

def search_zapier(page: Page, request: ZapierRequest) -> ZapierResult:
    url = "https://zapier.com/apps/google-sheets/integrations"
    checkpoint("Navigate to Zapier integrations")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = ZapierResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: Description → (optional "Premium"/...) → "Details" → "Try it" → "App1, App2" → "App1 + App2"
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'Details' && i + 1 < lines.length && lines[i+1] === 'Try it') {
                // Walk back to find the description (name)
                let nameIdx = i - 1;
                // Skip "Premium", "Premium apps: ..." lines
                while (nameIdx >= 0 && (lines[nameIdx] === 'Premium' || lines[nameIdx].startsWith('Premium apps:'))) {
                    nameIdx--;
                }
                if (nameIdx < 0) continue;
                const name = lines[nameIdx];
                // Apps are right after "Try it"
                const apps = (i + 2 < lines.length) ? lines[i + 2] : '';
                if (!name || name.length < 10) continue;
                results.push({ name, apps });
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = ZapItem()
        item.name = d.get("name", "")
        item.apps = d.get("apps", "")
        result.zaps.append(item)

    print(f"\nFound {len(result.zaps)} zaps:")
    for i, z in enumerate(result.zaps, 1):
        print(f"  {i}. {z.name[:70]} | Apps: {z.apps}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("zapier")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_zapier(page, ZapierRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
