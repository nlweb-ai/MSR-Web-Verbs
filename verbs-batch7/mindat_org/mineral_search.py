"""
Auto-generated Playwright script (Python)
Mindat.org – Mineral search and data extraction

Uses CDP-launched Chrome to avoid bot detection.
Search → mineral detail page → extract properties. If variety page, follows parent for crystal system & hardness.
"""

import os, sys, shutil, re, urllib.parse
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class MineralSearchRequest:
    query: str = "amethyst"


@dataclass
class MineralInfo:
    name: str = ""
    formula: str = ""
    crystal_system: str = ""
    hardness: str = ""
    color: str = ""
    localities: List[str] = field(default_factory=list)


@dataclass
class MineralSearchResult:
    mineral: MineralInfo = field(default_factory=MineralInfo)



def mineral_search(page: Page, request: MineralSearchRequest) -> MineralSearchResult:
    """Search Mindat for a mineral and extract properties."""
    print(f"  Query: {request.query}\n")

    checkpoint("Search Mindat")
    q = urllib.parse.quote_plus(request.query)
    page.goto(
        f"https://www.mindat.org/search.php?search={q}",
        wait_until="domcontentloaded",
    )
    page.wait_for_timeout(6000)

    checkpoint("Extract mineral info from page")
    info = page.evaluate(r"""() => {
        const body = document.body.innerText;

        // Name from h1
        const h1 = document.querySelector('h1');
        const name = h1 ? h1.textContent.trim() : '';

        // Parse properties - format: "Formula:SiO2Colour:...Lustre:VitreousHardness:7..."
        const formulaM = body.match(/Formula:\s*([^\n]+?)(?=Colour|Lustre|Hardness|Specific|Crystal|Member|Name:|$)/);
        const colorM = body.match(/Colour:\s*([^\n]+?)(?=Lustre|Hardness|Specific|Crystal|Member|Name:|Formula|$)/);
        const hardnessM = body.match(/Hardness:\s*([\d.–-]+)/);
        const crystalM = body.match(/Crystal\s*System:\s*([A-Za-z]+)/);

        // Variety info
        const varietyM = body.match(/[Vv]ariety of\s+(\w+)/);
        const parentMineral = varietyM ? varietyM[1] : '';

        // Localities - look for photo captions with location info
        const localities = [];
        const locMatches = body.matchAll(/\n([A-Z][^,\n]+(?:,\s*[A-Z][^,\n]+){2,})\n/g);
        for (const lm of locMatches) {
            const loc = lm[1].trim();
            // Filter out references and copyright lines
            if (loc.length > 15 && loc.length < 200 && !loc.includes('\u00a9') && !loc.match(/\(\d{4}\)/) && !loc.includes('Transactions')) {
                localities.push(loc);
                if (localities.length >= 5) break;
            }
        }

        return {
            name: name,
            formula: formulaM ? formulaM[1].trim() : '',
            color: colorM ? colorM[1].trim() : '',
            hardness: hardnessM ? hardnessM[1] : '',
            crystal_system: crystalM ? crystalM[1] : '',
            parent_mineral: parentMineral,
            localities: localities
        };
    }""")

    result = MineralSearchResult()
    m = result.mineral
    m.name = info.get("name", "")
    m.formula = info.get("formula", "")
    m.color = info.get("color", "")
    m.crystal_system = info.get("crystal_system", "")
    m.hardness = info.get("hardness", "")
    m.localities = info.get("localities", [])

    # For variety pages, note the parent mineral
    parent = info.get("parent_mineral", "")
    if parent and not m.crystal_system:
        m.crystal_system = f"(see parent: {parent})"
    if parent and not m.hardness:
        m.hardness = f"(see parent: {parent})"

    print(f"  Name:           {m.name}")
    print(f"  Formula:        {m.formula}")
    print(f"  Crystal System: {m.crystal_system}")
    print(f"  Hardness:       {m.hardness}")
    print(f"  Color:          {m.color}")
    print(f"  Localities:")
    for loc in m.localities:
        print(f"    - {loc}")
    print()

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("mindat")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = MineralSearchRequest()
            result = mineral_search(page, request)
            print(f"\n=== DONE ===")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
