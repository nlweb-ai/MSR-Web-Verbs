"""
Auto-generated Playwright script (Python)
Etymonline – Word Etymology
Word: "algorithm"

Generated on: 2026-04-18T05:15:10.643Z
Recorded 2 browser interactions
"""

import re
import os, sys, shutil
from dataclasses import dataclass
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class EtymologyRequest:
    word: str = "algorithm"


@dataclass
class EtymologyResult:
    word: str = ""
    origin_language: str = ""
    earliest_date: str = ""
    description: str = ""


def etymonline_search(page: Page, request: EtymologyRequest) -> EtymologyResult:
    """Look up word etymology on Etymonline."""
    print(f"  Word: {request.word}\n")

    # ── Step 1: Navigate to the word page ─────────────────────────────
    url = f"https://www.etymonline.com/word/{quote_plus(request.word.lower())}"
    print(f"Loading {url}...")
    checkpoint("Navigate to Etymonline word page")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # ── Step 2: Extract etymology data ────────────────────────────────
    checkpoint("Extract etymology data")
    data = page.evaluate(r"""(searchWord) => {
        const text = document.body.innerText;
        const result = {};

        // Word and part of speech - look for "word(n.)" pattern near the search word
        const wordRegex = new RegExp('(' + searchWord + ')\\s*\\(([^)]+)\\)', 'i');
        const wordMatch = text.match(wordRegex);
        if (wordMatch) {
            result.word = wordMatch[1].trim();
            result.pos = wordMatch[2].trim();
        } else {
            result.word = searchWord;
        }

        // Find the etymology section - text after "word(pos)" and before "Entries linking to"
        const entryStart = text.indexOf(result.word + '(');
        const entryEnd = text.indexOf('Entries linking to');
        const mainSection = entryStart >= 0 ? text.slice(entryStart, entryEnd > entryStart ? entryEnd : entryStart + 1000) : '';

        // Earliest date
        const dateMatch = mainSection.match(/\b(\d{4}s?)\b/);
        if (dateMatch) result.date = dateMatch[1];

        // Origin language
        const langMatch = mainSection.match(/from\s+(French|Latin|Greek|Old English|Arabic|Medieval Latin|Old French|Germanic|Sanskrit|Proto-Germanic|Middle English)\b/i);
        if (langMatch) result.origin_language = langMatch[1];

        // Full etymology description - text after the "word(pos)\n\n" line
        if (mainSection) {
            // Skip the "word(pos)" header line
            const descStart = mainSection.indexOf('\n\n');
            if (descStart > 0) {
                let desc = mainSection.slice(descStart).trim();
                result.description = desc.slice(0, 500);
            } else {
                // No double newline, just skip past the pos marker
                const posEnd = mainSection.indexOf(')');
                if (posEnd > 0) {
                    result.description = mainSection.slice(posEnd + 1).trim().slice(0, 500);
                }
            }
        }

        return result;
    }""", request.word)

    result = EtymologyResult(
        word=data.get("word", request.word),
        origin_language=data.get("origin_language", ""),
        earliest_date=data.get("date", ""),
        description=data.get("description", ""),
    )

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Etymonline: {result.word}")
    print("=" * 60)
    print(f"  Word:            {result.word}")
    if data.get("pos"):
        print(f"  Part of Speech:  {data['pos']}")
    print(f"  Earliest Date:   {result.earliest_date}")
    print(f"  Origin Language: {result.origin_language}")
    print(f"\n  Etymology:")
    print(f"  {result.description}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("etymonline_com")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = etymonline_search(page, EtymologyRequest())
            print(f"\nReturned etymology for {result.word}")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
