"""
MUBI – Now Showing Films

Browse MUBI's current film selection (Now Showing page) and extract
film title, director, year, country of origin, and description.
"""

import os, sys, re, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws


@dataclass(frozen=True)
class Request:
    max_results: int = 5


@dataclass
class Film:
    title: str = ""
    director: str = ""
    year: str = ""
    country: str = ""
    description: str = ""


@dataclass
class Result:
    films: List[Film] = field(default_factory=list)


def now_showing(page, request: Request) -> Result:
    """Navigate to MUBI Now Showing page and extract current films."""
    page.goto("https://mubi.com/en/showing", wait_until="domcontentloaded")
    page.wait_for_timeout(6000)

    data = page.evaluate(r"""(maxResults) => {
        const films = [];

        // Collect film cards from the "MUBI Releases" section.
        // Each card is wrapped in an <a> with href containing "/films/".
        // The poster image's alt text holds the film title.
        // Director, country, year, and description are in nearby elements.
        const links = document.querySelectorAll('a[href*="/films/"]');
        const seenSlugs = new Set();
        const containers = [];

        for (const link of links) {
            const slug = link.getAttribute('href');
            if (!slug || seenSlugs.has(slug)) continue;
            seenSlugs.add(slug);

            // Walk up to find the card container (parent or grandparent)
            let container = link.parentElement;
            for (let i = 0; i < 5; i++) {
                if (!container) break;
                const text = container.innerText || '';
                if (text.length > 80 && /\d{4}/.test(text)) {
                    containers.push({ container, slug });
                    break;
                }
                container = container.parentElement;
            }
        }

        for (const { container, slug } of containers) {
            if (films.length >= maxResults) break;

            const text = container.innerText || '';
            const lines = text.split('\n').map(l => l.trim()).filter(Boolean);

            // Title from poster img alt
            const img = container.querySelector('img[alt]');
            let title = '';
            if (img && img.alt && !img.alt.includes('badge') && !img.alt.includes('Winner')) {
                title = img.alt;
            }
            if (!title) {
                // Fallback: derive from slug
                const m = slug.match(/\/films\/(.+)/);
                if (m) title = m[1].replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            }

            // Director + country + year parsing.
            // Two layouts:
            // Multi-line: "DIRECTOR  COUNTRY YEAR" on a separate line
            // Single-line: "Director  Country YEARDirector  Country YEARWATCHDescription..."
            let director = '', country = '', year = '';
            const countryPatterns = [
                'UNITED STATES', 'UNITED KINGDOM', 'SOUTH KOREA', 'SOUTH AFRICA',
                'NEW ZEALAND', 'CZECH REPUBLIC', 'HONG KONG',
            ];
            const countryPatternsLower = countryPatterns.map(c =>
                c.split(' ').map(w => w[0] + w.slice(1).toLowerCase()).join(' ')
            );

            function parseDirectorLine(text) {
                // Try "Name  Country Year" with double-space separator
                const m2 = text.match(/^(.+?)\s{2,}(.+?)\s+(\d{4})/);
                if (m2) return { director: m2[1].trim(), country: m2[2].trim(), year: m2[3] };
                // Try "NAME COUNTRY YEAR" with known multi-word countries
                const allCountries = countryPatterns.concat(countryPatternsLower);
                for (const cp of allCountries) {
                    const idx = text.indexOf(cp);
                    if (idx > 0) {
                        const after = text.slice(idx + cp.length).trim();
                        const ym = after.match(/^(\d{4})/);
                        if (ym) return { director: text.slice(0, idx).trim(), country: cp, year: ym[1] };
                    }
                }
                // Single-word country: "NAME COUNTRY YEAR"
                const m1 = text.match(/^(.+)\s+([A-Za-z]+)\s+(\d{4})/);
                if (m1) return { director: m1[1].trim(), country: m1[2].trim(), year: m1[3] };
                return null;
            }

            // Try multi-line first

            // Handle hero card: "DIRECTED BY NAME" + "COUNTRY YEAR"
            for (let li = 0; li < lines.length; li++) {
                const dm = lines[li].match(/^DIRECTED BY (.+)/);
                if (dm && li + 1 < lines.length) {
                    const ym = lines[li + 1].match(/^(.+)\s+(\d{4})$/);
                    if (ym) {
                        director = dm[1].trim();
                        country = ym[1].trim();
                        year = ym[2];
                        break;
                    }
                }
            }

            // Normal parsing if hero card didn't match
            if (!director) {
                for (const line of lines) {
                    const r = parseDirectorLine(line);
                    if (r && r.director) {
                        director = r.director;
                        country = r.country;
                        year = r.year;
                        break;
                    }
                }
            }

            // Description: longest line that's not director/country/year and not a label
            // For single-line cards, extract text after "WATCH"
            let description = '';
            for (const line of lines) {
                // Single-line card: everything is one line with "WATCH" separator
                const watchIdx = line.indexOf('WATCH');
                if (watchIdx > 0 && line.length > 200) {
                    description = line.slice(watchIdx + 5).trim();
                    if (description.startsWith('ING')) description = ''; // skip "WATCHING"
                    continue;
                }
                if (line === 'WATCH' || line === 'WATCH NOW' || line === 'SEE ALL') continue;
                if (line === director || line === title.toUpperCase()) continue;
                if (/^\d{4}$/.test(line)) continue;
                if (/^MUBI/.test(line) && line.length < 30) continue;
                if (/^DIRECTED BY/.test(line)) continue;
                if (/clicking.*Watch now/.test(line)) continue;
                if (/Terms of Service/.test(line)) continue;
                if (/^Try \d+ days free/.test(line)) continue;
                if (line === 'WINNER' || line === 'SPECIAL JURY PRIZE') continue;
                if (line.length > 60 && line.length > description.length) {
                    description = line;
                }
            }

            if (title && (director || description)) {
                films.push({ title, director, year, country, description });
            }
        }

        return films;
    }""", request.max_results)

    result = Result()
    for f in data:
        result.films.append(Film(
            title=f.get("title", ""),
            director=f.get("director", ""),
            year=f.get("year", ""),
            country=f.get("country", ""),
            description=f.get("description", ""),
        ))
    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("mubi_now_showing")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            req = Request(max_results=5)
            result = now_showing(page, req)
            print(f"\nFound {len(result.films)} films on MUBI Now Showing:\n")
            for i, f in enumerate(result.films, 1):
                print(f"  {i}. {f.title}")
                print(f"     Director: {f.director}")
                print(f"     Year: {f.year} | Country: {f.country}")
                print(f"     Description: {f.description[:120]}...")
                print()
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
