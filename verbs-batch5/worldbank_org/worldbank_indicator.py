"""
Auto-generated Playwright script (Python)
World Bank – Economic Indicator Lookup
Country: "Germany", Indicator: "GDP per capita"

Generated on: 2026-04-18T03:01:42.301Z
Recorded 2 browser interactions

Uses Playwright's native locator API with the user's Chrome profile.
"""

import re
import os, sys, shutil
from dataclasses import dataclass, field
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class WorldBankRequest:
    indicator: str = "GDP per capita"
    country: str = "Germany"
    country_slug: str = "germany"
    max_related: int = 5


@dataclass
class IndicatorResult:
    country_name: str = ""
    indicator_name: str = ""
    most_recent_value: str = ""
    year: str = ""
    related_indicators: list = field(default_factory=list)


@dataclass
class RelatedIndicator:
    name: str = ""
    value: str = ""
    year: str = ""


def worldbank_lookup(page: Page, request: WorldBankRequest) -> IndicatorResult:
    """Look up an economic indicator on World Bank Data."""
    print(f"  Country: {request.country}")
    print(f"  Indicator: {request.indicator}\n")

    # ── Navigate to country page ──────────────────────────────────────
    country_url = f"https://data.worldbank.org/country/{request.country_slug}"
    print(f"Loading {country_url}...")
    checkpoint("Navigate to World Bank country page")
    page.goto(country_url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    # ── Scroll to load all sections ───────────────────────────────────
    for _ in range(3):
        page.evaluate("window.scrollBy(0, 2000)")
        page.wait_for_timeout(1000)

    # ── Extract indicator data ────────────────────────────────────────
    data = page.evaluate(r"""(args) => {
        const { indicator, maxRelated } = args;
        const text = document.body.innerText;

        // Split text into lines
        const lines = text.split('\n').map(l => l.trim()).filter(l => l);

        // Find the target indicator line
        let targetIdx = -1;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i].toLowerCase().includes(indicator.toLowerCase())) {
                targetIdx = i;
                break;
            }
        }

        let indicatorName = '';
        let mostRecentValue = '';
        let year = '';

        if (targetIdx >= 0) {
            indicatorName = lines[targetIdx];
            // Look for value and year in surrounding lines
            // Pattern: value appears as a number, year as (YYYY) or (YYYY something)
            for (let i = targetIdx + 1; i < Math.min(targetIdx + 15, lines.length); i++) {
                const line = lines[i];
                // Match a number value (with commas, decimals)
                if (!mostRecentValue && /^[\d,.]+$/.test(line)) {
                    mostRecentValue = line;
                }
                // Match year in parentheses like (2024) or (2024 trillion)
                const yearMatch = line.match(/^\(?(\d{4})\b/);
                if (!year && yearMatch && mostRecentValue) {
                    year = yearMatch[1];
                    break;
                }
            }
        }

        // Find related indicators in the Economic section
        const related = [];
        let econIdx = -1;
        for (let i = 0; i < lines.length; i++) {
            if (lines[i] === 'Economic' && i + 3 < lines.length &&
                lines[i + 1] === 'Indicator' && lines[i + 2] === 'Most recent value') {
                econIdx = i;
                break;
            }
        }

        if (econIdx >= 0) {
            let startIdx = econIdx;
            for (let i = econIdx; i < Math.min(econIdx + 5, lines.length); i++) {
                if (lines[i] === 'Trend') { startIdx = i + 1; break; }
            }

            for (let i = startIdx; i < lines.length && related.length < maxRelated; i++) {
                const line = lines[i];
                if (line.toLowerCase().includes(indicator.toLowerCase())) continue;
                if (/^\(/.test(line) || line === line.toUpperCase()) continue;
                if (/\(.*(?:%|\$|US|PPP|years|trillion)/.test(line) && line.length > 10 && line.length < 100) {
                    let relValue = '';
                    let relYear = '';
                    for (let j = i + 1; j < Math.min(i + 20, lines.length); j++) {
                        if (/^(current|constant)\s+(US\$|LCU)$/i.test(lines[j])) continue;
                        if (!relValue && /^[\d,.\-]+$/.test(lines[j])) {
                            relValue = lines[j];
                        }
                        const ym = lines[j].match(/^\(?(\d{4})\b/);
                        if (!relYear && ym && relValue) {
                            relYear = ym[1];
                            break;
                        }
                    }
                    if (relValue && relYear) {
                        related.push({ name: line, value: relValue, year: relYear });
                    }
                }
                if (/^(Environment|Institutions|Social)$/.test(line)) break;
            }
        }

        return { indicatorName, mostRecentValue, year, related };
    }""", {"indicator": request.indicator, "maxRelated": request.max_related})

    # ── Print results ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"World Bank: {request.country}")
    print("=" * 60)
    print(f"\n  Indicator: {data['indicatorName']}")
    print(f"  Value:     {data['mostRecentValue']}")
    print(f"  Year:      {data['year']}")

    if data['related']:
        print(f"\n  Related Economic Indicators:")
        for r in data['related']:
            print(f"    - {r['name']}: {r['value']} ({r['year']})")

    result = IndicatorResult(
        country_name=request.country,
        indicator_name=data['indicatorName'],
        most_recent_value=data['mostRecentValue'],
        year=data['year'],
        related_indicators=[RelatedIndicator(**r) for r in data['related']],
    )
    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("worldbank_org")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = worldbank_lookup(page, WorldBankRequest())
            print(f"\nReturned: {result.indicator_name} = {result.most_recent_value} ({result.year})")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
