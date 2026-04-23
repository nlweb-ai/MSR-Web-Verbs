"""
Playwright script (Python) — Pluto TV Channels
Browse Pluto TV news channels.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class PlutoRequest:
    category: str = "News"
    max_results: int = 5


@dataclass
class ChannelItem:
    current_program: str = ""
    time_remaining: str = ""
    next_program: str = ""


@dataclass
class PlutoResult:
    channels: List[ChannelItem] = field(default_factory=list)


# Browses Pluto TV live guide and extracts current program,
# time remaining, and next program.
def get_pluto_channels(page: Page, request: PlutoRequest) -> PlutoResult:
    url = "https://pluto.tv/live-tv"
    print(f"Loading {url}...")
    checkpoint("Navigate to Pluto TV")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(10000)

    result = PlutoResult()

    checkpoint("Extract channel listings")
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find 'Live TV Guide' marker
        let start = 0;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === 'Live TV Guide') { start = i + 1; break; }
        }
        // Parse channel blocks: "Channel", "Now HH:MM", ShowName, "X min left", "On Next:", NextShow, ...
        for (let i = start; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'Channel' && i + 4 < lines.length) {
                const current_program = lines[i + 2] || '';
                let time_remaining = '';
                let next_program = '';
                let j = i + 3;
                if (j < lines.length && /left$/.test(lines[j])) {
                    time_remaining = lines[j];
                    j++;
                }
                if (j < lines.length && lines[j] === 'On Next:' && j + 1 < lines.length) {
                    next_program = lines[j + 1];
                }
                if (current_program && !/^Now /.test(current_program)) {
                    results.push({ current_program, time_remaining, next_program });
                }
                i += 6;
            }
        }
        return results;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = ChannelItem()
        item.current_program = d.get("current_program", "")
        item.time_remaining = d.get("time_remaining", "")
        item.next_program = d.get("next_program", "")
        result.channels.append(item)

    print(f"\nFound {len(result.channels)} channels:")
    for i, c in enumerate(result.channels, 1):
        print(f"\n  {i}. {c.current_program}")
        print(f"     {c.time_remaining} | Next: {c.next_program}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("pluto")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = get_pluto_channels(page, PlutoRequest())
            print("\n=== DONE ===")
            print(f"Found {len(result.channels)} channels")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
