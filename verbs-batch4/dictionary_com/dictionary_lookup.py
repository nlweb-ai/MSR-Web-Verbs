import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class DictionaryLookupRequest:
    word: str = "ephemeral"

@dataclass(frozen=True)
class DictionaryLookupResult:
    word: str = ""
    pronunciation: str = ""
    part_of_speech: str = ""
    primary_definition: str = ""
    example_sentence: str = ""
    synonyms: list = None  # list[str]

# Search for a word on Dictionary.com and extract its pronunciation, part of speech,
# primary definition, example sentence, and up to 3 synonyms.
def dictionary_lookup(page: Page, request: DictionaryLookupRequest) -> DictionaryLookupResult:
    word = request.word
    print(f"  Word to look up: {word}\n")

    url = f"https://www.dictionary.com/browse/{word}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to {url}")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    print(f"  Loaded: {page.url}")

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""

    result_word = word
    pronunciation = "N/A"
    part_of_speech = "N/A"
    primary_definition = "N/A"
    example_sentence = "N/A"
    synonyms = []

    # --- Extract pronunciation ---
    try:
        pron_el = page.locator('[class*="pron"], [class*="pronunciation"], span.pron-spell-content')
        if pron_el.count() > 0:
            pronunciation = pron_el.first.inner_text(timeout=3000).strip()
    except Exception:
        pass
    if pronunciation == "N/A":
        pm = re.search(r'\[([^\]]+)\]', body_text)
        if not pm:
            pm = re.search(r'/([^/]+)/', body_text)
        if pm:
            pronunciation = pm.group(0).strip()

    # --- Extract part of speech ---
    try:
        pos_el = page.locator('[class*="pos"], [class*="part-of-speech"], .luna-pos')
        if pos_el.count() > 0:
            part_of_speech = pos_el.first.inner_text(timeout=3000).strip()
    except Exception:
        pass
    if part_of_speech == "N/A":
        pos_match = re.search(
            r'\b(noun|verb|adjective|adverb|pronoun|preposition|conjunction|interjection)\b',
            body_text, re.I
        )
        if pos_match:
            part_of_speech = pos_match.group(0).strip().lower()

    # --- Extract primary definition ---
    try:
        def_el = page.locator('[class*="def-content"], [class*="definition"], [value="1"] + span')
        if def_el.count() > 0:
            primary_definition = def_el.first.inner_text(timeout=3000).strip()
            # Clean trailing colons or semicolons
            primary_definition = re.sub(r'^[\d.)\s]+', '', primary_definition).strip()
    except Exception:
        pass
    if primary_definition == "N/A":
        # Fallback: grab text after part of speech line
        lines = [l.strip() for l in body_text.split("\n") if l.strip()]
        for i, line in enumerate(lines):
            if re.search(r'\b(noun|verb|adjective|adverb)\b', line, re.I) and len(line) < 30:
                # Next non-empty line is likely the first definition
                for j in range(i + 1, min(i + 5, len(lines))):
                    candidate = lines[j].strip()
                    if len(candidate) > 10 and not re.match(r'^\d+$', candidate):
                        primary_definition = re.sub(r'^[\d.)\s]+', '', candidate).strip()
                        break
                break

    # --- Extract example sentence ---
    try:
        ex_el = page.locator('[class*="example"], [class*="luna-example"]')
        if ex_el.count() > 0:
            example_sentence = ex_el.first.inner_text(timeout=3000).strip()
    except Exception:
        pass
    if example_sentence == "N/A":
        em = re.search(r'(?:example[:\s]*)(.*)', body_text, re.I)
        if em:
            example_sentence = em.group(1).strip()

    # --- Extract synonyms (up to 3) ---
    try:
        syn_el = page.locator('[class*="synonym"] a, [class*="thesaurus"] a, [data-type="synonym"] a')
        syn_count = syn_el.count()
        if syn_count > 0:
            for i in range(min(syn_count, 3)):
                s = syn_el.nth(i).inner_text(timeout=3000).strip()
                if s and s.lower() != word.lower():
                    synonyms.append(s)
    except Exception:
        pass
    if not synonyms:
        sm = re.search(r'synonym[s]?[:\s]*([\w,\s]+)', body_text, re.I)
        if sm:
            raw = [s.strip() for s in sm.group(1).split(",") if s.strip()]
            synonyms = raw[:3]

    print("=" * 60)
    print(f"Dictionary.com – {result_word}")
    print("=" * 60)
    print(f"  Word:          {result_word}")
    print(f"  Pronunciation: {pronunciation}")
    print(f"  Part of speech:{part_of_speech}")
    print(f"  Definition:    {primary_definition}")
    print(f"  Example:       {example_sentence}")
    print(f"  Synonyms:      {', '.join(synonyms) if synonyms else 'N/A'}")

    return DictionaryLookupResult(
        word=result_word,
        pronunciation=pronunciation,
        part_of_speech=part_of_speech,
        primary_definition=primary_definition,
        example_sentence=example_sentence,
        synonyms=synonyms,
    )

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = dictionary_lookup(page, DictionaryLookupRequest())
        print(f"\nWord: {result.word}")
        print(f"Synonyms found: {len(result.synonyms or [])}")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
