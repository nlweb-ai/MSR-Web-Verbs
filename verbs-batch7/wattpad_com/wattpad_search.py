"""
Auto-generated Playwright script (Python)
Wattpad – Story Search

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
class SearchRequest:
    search_query: str = "fantasy adventure"
    max_results: int = 5


@dataclass
class StoryResult:
    title: str = ""
    reads: str = ""
    votes: str = ""
    parts: str = ""
    description: str = ""


@dataclass
class SearchResult:
    stories: List[StoryResult] = field(default_factory=list)


def wattpad_search(page: Page, request: SearchRequest) -> SearchResult:
    """Search Wattpad for stories."""
    print(f"  Query: {request.search_query}\n")

    query_encoded = request.search_query.replace(" ", "%20")
    url = f"https://www.wattpad.com/search/{query_encoded}"
    print(f"Loading {url}...")
    checkpoint("Navigate to search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = SearchResult()

    checkpoint("Extract story results")
    js_code = r"""(max) => {
        const lines = document.body.innerText.split('\n').map(l => l.trim()).filter(l => l.length > 0);
        // Find start - after tag refinement section
        // Look for first story title (appears twice - once in heading, once in link)
        // Pattern: Title (repeated), Complete/Ongoing, Reads, count, shortCount, Votes, count, shortCount, Parts, count, shortCount, Time, duration, longDuration, shortDuration, description
        const stories = [];
        let i = 0;
        // Skip header/filter section - find "Refine by tag" then skip tags
        for (; i < lines.length; i++) {
            if (lines[i] === 'Refine by tag') { i++; break; }
        }
        // Skip tag names - look for the first line that appears twice consecutively (story title pattern)
        while (i < lines.length - 1) {
            if (lines[i] === lines[i + 1] && lines[i].length > 3) break;
            i++;
        }
        while (i < lines.length && stories.length < max) {
            // Title appears twice consecutively
            const title = lines[i]; i++;
            if (!title || title.length < 3) break;
            // Skip duplicate title
            if (i < lines.length && lines[i] === title) i++;
            // Skip Complete/Ongoing (may appear twice)
            while (i < lines.length && (lines[i] === 'Complete' || lines[i] === 'Ongoing')) i++;
            // Now parse structured fields: Reads, Votes, Parts, Time
            // Each can appear as "Reads" then "Reads NNN" then NNN then shortNNN
            let reads = '', votes = '', parts = '';
            // Reads
            while (i < lines.length && lines[i].startsWith('Reads')) i++;
            if (i < lines.length && /^[\d,]+$/.test(lines[i])) i++;
            if (i < lines.length && /^[\d.]+[KM]?$/.test(lines[i])) { reads = lines[i]; i++; }
            else if (i < lines.length && /^[\d,]+$/.test(lines[i])) { reads = lines[i]; i++; }
            // Votes
            while (i < lines.length && lines[i].startsWith('Votes')) i++;
            if (i < lines.length && /^[\d,]+$/.test(lines[i])) i++;
            if (i < lines.length && /^[\d,.]+[KM]?$/.test(lines[i])) { votes = lines[i]; i++; }
            else if (i < lines.length && /^[\d,]+$/.test(lines[i])) { votes = lines[i]; i++; }
            // Parts
            while (i < lines.length && lines[i].startsWith('Parts')) i++;
            if (i < lines.length && /^\d+$/.test(lines[i])) { parts = lines[i]; i++; }
            if (i < lines.length && /^\d+$/.test(lines[i])) i++; // skip duplicate
            // Time
            while (i < lines.length && lines[i].startsWith('Time')) i++;
            while (i < lines.length && (/^\d+h\s*\d*m?$/.test(lines[i]) || /^\d+ hours?/.test(lines[i]) || /^\d+m$/.test(lines[i]) || /^\d+ minutes?/.test(lines[i]))) i++;
            // Description
            let description = '';
            if (i < lines.length && lines[i].length > 30) {
                description = lines[i].substring(0, 200);
                i++;
            }
            if (title && title.length > 5) {
                stories.push({title, reads, votes, parts, description});
            }
        }
        return stories;
    }"""
    stories_data = page.evaluate(js_code, request.max_results)

    for sd in stories_data:
        s = StoryResult()
        s.title = sd.get("title", "")
        s.reads = sd.get("reads", "")
        s.votes = sd.get("votes", "")
        s.parts = sd.get("parts", "")
        s.description = sd.get("description", "")
        result.stories.append(s)

    for i, s in enumerate(result.stories, 1):
        print(f"\n  Story {i}:")
        print(f"    Title:  {s.title}")
        print(f"    Reads:  {s.reads}")
        print(f"    Votes:  {s.votes}")
        print(f"    Parts:  {s.parts}")
        print(f"    Desc:   {s.description[:80]}...")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("wattpad")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = SearchRequest()
            result = wattpad_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.stories)} stories")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
