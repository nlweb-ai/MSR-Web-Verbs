import os
import sys
import shutil
from dataclasses import dataclass, field
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class TVGuideSearchRequest:
    search_query: str = "drama"
    max_results: int = 5


@dataclass
class TVGuideShowItem:
    show_title: str = ""
    air_time: str = ""
    network: str = ""


@dataclass
class TVGuideSearchResult:
    shows: List[TVGuideShowItem] = field(default_factory=list)
    error: str = ""


def tvguide_search(page, request: TVGuideSearchRequest) -> TVGuideSearchResult:
    result = TVGuideSearchResult()
    try:
        url = f"https://www.tvguide.com/tvshows/"
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(5000)

        checkpoint("Page loaded")

        shows_data = page.evaluate("""(max) => {
            const results = [];
            const body = document.body.innerText;
            const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            let inLiveTV = false;
            for (let i = 0; i < lines.length && results.length < max; i++) {
                if (lines[i] === 'Live TV') { inLiveTV = true; continue; }
                if (inLiveTV && (lines[i] === 'TV and Movie Recommendations' || lines[i].startsWith('Hand-picked'))) break;
                if (inLiveTV && lines[i] === 'See Full Schedule') continue;
                if (inLiveTV && i + 1 < lines.length) {
                    // Pattern: ShowName then "SxxExx · TIME · NETWORK" or "TIME · NETWORK"
                    const infoLine = lines[i + 1];
                    const parts = infoLine.split('\\u00b7').map(p => p.trim());
                    if (parts.length >= 2 && /\\d+:\\d+/.test(infoLine)) {
                        const show_title = lines[i];
                        // Time could be in parts[0] or parts[1] (if season info first)
                        let air_time = '', network = '';
                        for (const p of parts) {
                            if (/\\d+:\\d+/.test(p)) air_time = p;
                            else if (!/^S\\d+/.test(p)) network = p;
                        }
                        results.push({ show_title, air_time, network });
                        i++; // skip the info line
                    }
                }
            }
            return results;
        }""", request.max_results)

        for item in shows_data[:request.max_results]:
            result.shows.append(TVGuideShowItem(**item))

        checkpoint(f"Extracted {len(result.shows)} shows")

    except Exception as e:
        result.error = str(e)
    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir()
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(ws_url)
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()

    try:
        request = TVGuideSearchRequest()
        result = tvguide_search(page, request)
        print(f"\nFound {len(result.shows)} shows:")
        for i, s in enumerate(result.shows):
            print(f"  {i+1}. {s.show_title} - {s.air_time} on {s.network}")
        if result.error:
            print(f"Error: {result.error}")
    finally:
        browser.close()
        pw.stop()
        chrome_proc.terminate()
        shutil.rmtree(profile_dir, ignore_errors=True)


def run_with_debugger():
    test_func()


if __name__ == "__main__":
    run_with_debugger()
