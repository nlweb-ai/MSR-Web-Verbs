import os
import sys
import shutil
from dataclasses import dataclass, field
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class TVTropesSearchRequest:
    search_query: str = "plot twist"
    max_results: int = 5


@dataclass
class TVTropesTropeItem:
    trope_name: str = ""
    category: str = ""
    description: str = ""
    url: str = ""


@dataclass
class TVTropesSearchResult:
    tropes: List[TVTropesTropeItem] = field(default_factory=list)
    error: str = ""


def tvtropes_search(page, request: TVTropesSearchRequest) -> TVTropesSearchResult:
    result = TVTropesSearchResult()
    try:
        url = f"https://tvtropes.org/pmwiki/search_result.php?q={request.search_query}"
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)

        checkpoint("Search results loaded")

        tropes_data = page.evaluate("""(max) => {
            const links = document.querySelectorAll('a[href]');
            const items = [];
            const seen = new Set();
            for (const a of links) {
                if (items.length >= max) break;
                const href = a.getAttribute('href') || '';
                // Match tvtropes wiki pages like /pmwiki/pmwiki.php/Main/TropeName
                if (!href.match(/tvtropes\\.org\\/pmwiki\\/pmwiki\\.php\\/(Main|Literature|Film|Series|VideoGame|WesternAnimation|Anime|Manga|ComicBook|Fanfic|Music|Theatre|Podcast|WebAnimation|WebComic|WebVideo|Recap|Characters|YMMV|Trivia|Headscratchers|Laconic|PlayingWith|Analysis)\\/[A-Z]/)) continue;
                const text = a.textContent.trim();
                if (!text || text.length < 3 || text.length > 200) continue;
                if (seen.has(href)) continue;
                seen.add(href);
                // Extract namespace from URL
                const nsMatch = href.match(/pmwiki\\.php\\/([^/]+)\\//);
                const category = nsMatch ? nsMatch[1] : '';
                items.push({trope_name: text, category, description: '', url: href});
            }
            return items;
        }""", request.max_results)

        for item in tropes_data:
            result.tropes.append(TVTropesTropeItem(**item))

        checkpoint(f"Extracted {len(result.tropes)} tropes")

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
        request = TVTropesSearchRequest()
        result = tvtropes_search(page, request)
        print(f"Found {len(result.tropes)} tropes")
        for i, t in enumerate(result.tropes):
            print(f"  {i+1}. {t.trope_name} [{t.category}] - {t.description[:80]}")
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
