"""Playwright script (Python) — Typeform"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class TypeformRequest:
    query: str = "customer feedback"
    max_results: int = 5

@dataclass
class TemplateItem:
    name: str = ""
    description: str = ""

@dataclass
class TypeformResult:
    templates: List[TemplateItem] = field(default_factory=list)

def search_typeform(page: Page, request: TypeformRequest) -> TypeformResult:
    url = f"https://www.typeform.com/templates/?q={request.query.replace(' ', '+')}"
    checkpoint("Navigate to Typeform templates")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    result = TypeformResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: template name, description, "View template"
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'View template' && i >= 2) {
                const description = lines[i - 1];
                const name = lines[i - 2];
                // Skip section headers and nav items
                if (name.length > 10 && !name.startsWith('See more') && !name.startsWith('All templates')) {
                    results.push({ name, description });
                }
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = TemplateItem()
        item.name = d.get("name", "")
        item.description = d.get("description", "")
        result.templates.append(item)

    print(f"\nFound {len(result.templates)} templates:")
    for i, t in enumerate(result.templates, 1):
        print(f"  {i}. {t.name} - {t.description[:60]}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("typeform")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_typeform(page, TypeformRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
