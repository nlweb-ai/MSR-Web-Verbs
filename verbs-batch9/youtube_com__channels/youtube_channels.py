"""Playwright script (Python) — YouTube Channels"""
import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class YouTubeChannelsRequest:
    query: str = "science education"
    max_results: int = 5

@dataclass
class ChannelItem:
    name: str = ""
    subscribers: str = ""
    description: str = ""

@dataclass
class YouTubeChannelsResult:
    channels: List[ChannelItem] = field(default_factory=list)

def search_youtube_channels(page: Page, request: YouTubeChannelsRequest) -> YouTubeChannelsResult:
    url = f"https://www.youtube.com/results?search_query={request.query.replace(' ', '+')}&sp=EgIQAg%3D%3D"
    checkpoint("Navigate to YouTube channel search")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(8000)
    result = YouTubeChannelsResult()
    js_code = """(max) => {
        const results = [];
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
        // Pattern: Name → "@handle·X subscribers" → Description → "Subscribe"
        for (let i = 0; i < lines.length && results.length < max; i++) {
            if (lines[i] === 'Subscribe' && i >= 2) {
                // Walk back: optional description, @handle line, name
                let descIdx = i - 1;
                let handleIdx = -1;
                // Find @handle line
                for (let j = i - 1; j >= Math.max(0, i - 3); j--) {
                    if (lines[j].startsWith('@')) {
                        handleIdx = j;
                        break;
                    }
                }
                if (handleIdx < 1) continue;
                const name = lines[handleIdx - 1];
                if (!name || name.length < 3) continue;
                // Parse subscribers from handle line: "@handle·X subscribers"
                const handleLine = lines[handleIdx];
                let subscribers = '';
                const subMatch = handleLine.match(/[\\u00b7\\u2022](.+?subscribers)/i);
                if (subMatch) subscribers = subMatch[1].trim();
                // Description is between handle and Subscribe
                let description = '';
                if (handleIdx + 1 < i) {
                    description = lines[handleIdx + 1];
                }
                results.push({ name, subscribers, description });
            }
        }
        return results;
    }"""
    for d in page.evaluate(js_code, request.max_results):
        item = ChannelItem()
        item.name = d.get("name", "")
        item.subscribers = d.get("subscribers", "")
        item.description = d.get("description", "")
        result.channels.append(item)

    print(f"\nFound {len(result.channels)} channels:")
    for i, c in enumerate(result.channels, 1):
        print(f"  {i}. {c.name} - {c.subscribers} - {c.description[:60]}")
    return result

def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("youtube_channels")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            search_youtube_channels(page, YouTubeChannelsRequest())
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
