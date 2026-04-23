"""
Auto-generated Playwright script (Python)
Merriam-Webster – Dictionary Lookup
Word: "serendipity"

Generated on: 2026-04-18T15:13:49.196Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class WordRequest:
    word: str = "serendipity"


@dataclass
class WordResult:
    word: str = ""
    pronunciation: str = ""
    part_of_speech: str = ""
    definition: str = ""
    example: str = ""
    first_known_use: str = ""


def mw_lookup(page: Page, request: WordRequest) -> WordResult:
    """Look up a word on Merriam-Webster."""
    print(f"  Word: {request.word}\n")

    url = f"https://www.merriam-webster.com/dictionary/{request.word}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Merriam-Webster")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    checkpoint("Extract word data")
    body_text = page.evaluate("document.body.innerText") or ""

    word = request.word
    pronunciation = ""
    part_of_speech = ""
    definition = ""
    example = ""
    first_known_use = ""

    try:
        h1 = page.locator("h1.hword, h1").first
        if h1.is_visible(timeout=2000):
            word = h1.inner_text().strip()
    except Exception:
        pass

    try:
        pron = page.locator(".prons-entries-list-inline .pron-value, .pr").first
        if pron.is_visible(timeout=2000):
            pronunciation = pron.inner_text().strip()
    except Exception:
        pass

    try:
        pos = page.locator(".important-blue-link, .parts-of-speech a, .fl").first
        if pos.is_visible(timeout=2000):
            part_of_speech = pos.inner_text().strip()
    except Exception:
        pass

    try:
        defn = page.locator(".dtText, .sb-entry .sense .dt span").first
        if defn.is_visible(timeout=2000):
            definition = defn.inner_text().strip()[:300]
    except Exception:
        pass

    try:
        ex = page.locator(".sub-content-thread .ex-sent, .in-sentences .ex-sent").first
        if ex.is_visible(timeout=2000):
            example = ex.inner_text().strip()[:200]
    except Exception:
        pass

    fm = re.search(r"First Known Use.*?(\d{4})", body_text, re.IGNORECASE)
    if fm:
        first_known_use = fm.group(1)

    result = WordResult(
        word=word, pronunciation=pronunciation, part_of_speech=part_of_speech,
        definition=definition, example=example, first_known_use=first_known_use,
    )

    print("\n" + "=" * 60)
    print(f"Merriam-Webster: {result.word}")
    print("=" * 60)
    print(f"  Pronunciation:  {result.pronunciation}")
    print(f"  Part of Speech: {result.part_of_speech}")
    print(f"  Definition:     {result.definition[:80]}...")
    print(f"  Example:        {result.example[:80]}")
    print(f"  First Known Use: {result.first_known_use}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("merriam_webster_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = mw_lookup(page, WordRequest())
            print(f"\nReturned definition for {result.word}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
