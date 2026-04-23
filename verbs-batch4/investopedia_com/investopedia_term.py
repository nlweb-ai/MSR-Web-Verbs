import re
import os
from dataclasses import dataclass, field
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class InvestopediaTermRequest:
    query: str = "compound interest"

@dataclass(frozen=True)
class InvestopediaTermResult:
    term_name: str = ""
    definition: str = ""
    key_takeaways: list = None  # list[str]
    example: str = ""

# Search for a financial term on Investopedia, click the top result,
# and extract term name, definition, key takeaways, and example.
def investopedia_term(page: Page, request: InvestopediaTermRequest) -> InvestopediaTermResult:
    query = request.query
    print(f"  Search query: {query}\n")

    url = f"https://www.investopedia.com/search?q={quote_plus(query)}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to Investopedia search")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)
    print(f"  Loaded: {page.url}")

    # Click the first search result link
    first_result = page.locator(
        'a[class*="search-result"], '
        'a[class*="result-title"], '
        'a[class*="mntl-card"], '
        '#search-results__list a, '
        '[data-testid="search-results"] a, '
        'a[href*="investopedia.com/terms/"], '
        'a[href*="investopedia.com/articles/"]'
    ).first
    try:
        first_result.click(timeout=5000)
        page.wait_for_timeout(5000)
        print(f"  Navigated to article: {page.url}")
    except Exception as e:
        print(f"  Could not click first result: {e}")
        # Fallback: try any link in the search results area
        links = page.locator("a[href*='investopedia.com']")
        for i in range(links.count()):
            href = links.nth(i).get_attribute("href") or ""
            if "/terms/" in href or "/articles/" in href:
                links.nth(i).click(timeout=5000)
                page.wait_for_timeout(5000)
                print(f"  Navigated to article (fallback): {page.url}")
                break

    body_text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    lines = [l.strip() for l in body_text.split("\n") if l.strip()]

    term_name = ""
    definition = ""
    key_takeaways = []
    example = ""

    # Extract term name from h1
    h1 = page.locator("h1").first
    try:
        term_name = h1.inner_text(timeout=3000).strip()
    except Exception:
        for line in lines:
            if len(line) > 5 and len(line) < 200:
                term_name = line
                break

    # Extract definition — look for text after "What Is" or the first substantial paragraph
    in_definition = False
    for i, line in enumerate(lines):
        if re.search(r'what\s+is|definition', line, re.IGNORECASE):
            in_definition = True
            # If the "What Is" line itself has content after the heading
            if len(line) > 50:
                definition = line
                break
            continue
        if in_definition and len(line) > 40:
            definition = line
            break

    # Fallback: use first long paragraph if no definition found
    if not definition:
        for line in lines:
            if len(line) > 80 and line != term_name:
                definition = line
                break

    # Extract key takeaways — look for "Key Takeaways" section
    in_takeaways = False
    for i, line in enumerate(lines):
        if re.search(r'key\s+takeaways', line, re.IGNORECASE):
            in_takeaways = True
            continue
        if in_takeaways:
            # Stop at the next section heading or after 3 takeaways
            if len(key_takeaways) >= 3:
                break
            if re.match(r'^(Table of Contents|Understanding|Example|Formula|History|Special|The Bottom|How|Why|What|FAQs)', line):
                break
            if len(line) > 20:
                key_takeaways.append(line)

    # Extract example — look for "Example" section
    in_example = False
    for i, line in enumerate(lines):
        if re.search(r'^example', line, re.IGNORECASE):
            in_example = True
            continue
        if in_example and len(line) > 40:
            example = line
            break

    # Fallback: search for lines containing "for example" or "e.g."
    if not example:
        for line in lines:
            if re.search(r'for example|e\.g\.|for instance', line, re.IGNORECASE) and len(line) > 30:
                example = line
                break

    print("=" * 60)
    print(f"Investopedia - Term: \"{query}\"")
    print("=" * 60)
    print(f"\n  Term Name: {term_name}")
    print(f"  Definition: {definition[:200]}{'...' if len(definition) > 200 else ''}")
    print(f"  Key Takeaways ({len(key_takeaways)}):")
    for idx, kt in enumerate(key_takeaways, 1):
        print(f"    {idx}. {kt[:120]}{'...' if len(kt) > 120 else ''}")
    print(f"  Example: {example[:200]}{'...' if len(example) > 200 else ''}")

    return InvestopediaTermResult(
        term_name=term_name,
        definition=definition,
        key_takeaways=key_takeaways if key_takeaways else [],
        example=example,
    )

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = investopedia_term(page, InvestopediaTermRequest())
        print(f"\nTerm: {result.term_name}")
        print(f"Takeaways: {len(result.key_takeaways or [])}")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
