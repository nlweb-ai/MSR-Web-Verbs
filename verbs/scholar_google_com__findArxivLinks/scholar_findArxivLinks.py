"""
Auto-generated Playwright script (Python)
Google Scholar – Find Arxiv Links for a Paper
Paper: "Structural Temporal Logic for mechanized program verification" by Ioannidis

Generated on: 2026-03-19T22:09:34.931Z
Recorded 5 browser interactions

Uses Playwright with CDP temp profile (no login required).
"""
import re
import os, sys, shutil, tempfile, subprocess, json, time
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page
from urllib.request import urlopen

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, find_chrome_executable


@dataclass(frozen=True)
class ScholarPaperSearchRequest:
    paper_title: str
    author: str = ""
    max_results: int = 5


@dataclass(frozen=True)
class ScholarArxivLink:
    title: str
    arxiv_url: str


@dataclass(frozen=True)
class ScholarPaperSearchResult:
    paper_title: str
    author: str
    links: list[ScholarArxivLink]


# Searches Google Scholar for a paper by title (and optionally author),
# then returns any Arxiv links found for that paper.
def find_arxiv_links_for_paper(
    page: Page,
    request: ScholarPaperSearchRequest,
) -> ScholarPaperSearchResult:
    results = []

    try:
        # ── STEP 1: Navigate to Google Scholar ────────────────────────────
        print("STEP 1: Navigate to Google Scholar...")
        page.goto("https://scholar.google.com/", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        # Dismiss any cookie/consent banners
        for sel in [
            "button#onetrust-accept-btn-handler",
            "button:has-text('Accept all')",
            "button:has-text('I agree')",
            "button:has-text('Accept')",
            "[aria-label='Close']",
        ]:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=800):
                    btn.evaluate("el => el.click()")
                    page.wait_for_timeout(500)
            except Exception:
                pass

        # ── STEP 2: Enter search query ────────────────────────────────────
        query = request.paper_title
        if request.author:
            query += f" {request.author}"
        print(f'STEP 2: Search for "{query}"...')

        # Concretized: fill search input via JS and click search button
        page.evaluate("""(q) => {
            const input = document.getElementById('gs_hdr_tsi') || document.querySelector('input[name="q"]');
            if (input) {
                input.value = q;
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""", query)
        page.wait_for_timeout(500)

        page.evaluate("""() => {
            const btn = document.getElementById('gs_hdr_tsb') || document.querySelector('button[aria-label="Search"]');
            if (btn) btn.click();
            else { const form = document.querySelector('form'); if (form) form.submit(); }
        }""")
        print("  Submitted search")
        page.wait_for_timeout(3000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(2000)
        print(f"  URL: {page.url}")

        # ── STEP 3: Extract Arxiv links from results ─────────────────────
        print(f"STEP 3: Extract Arxiv links (up to {request.max_results})...")

        # Strategy 1: Find direct arxiv.org links on the search results page
        all_links = page.eval_on_selector_all(
            'a',
            'els => els.map(e => ({href: e.href, text: (e.textContent || "").trim().substring(0, 120)}))'
        )
        for link in all_links:
            href = link.get("href", "")
            text = link.get("text", "")
            if "arxiv.org" in href and len(results) < request.max_results:
                results.append({"title": text or "Arxiv Link", "arxiv_url": href})

        # Strategy 2: Check each result card for arxiv links
        if not results:
            print("  No direct arxiv links, checking result cards...")
            card_data = page.evaluate("""() => {
                const results = [];
                const cards = document.querySelectorAll('.gs_r.gs_or.gs_scl, .gs_ri, .gs_r');
                for (const card of cards) {
                    const titleEl = card.querySelector('h3 a, .gs_rt a');
                    if (!titleEl) continue;
                    const title = (titleEl.textContent || "").trim();
                    const url = titleEl.href;
                    const cardLinks = Array.from(card.querySelectorAll('a')).map(a => ({
                        href: a.href, text: (a.textContent || "").trim()
                    }));
                    results.push({ title, url, links: cardLinks });
                }
                return results;
            }""")
            for card in card_data:
                if "arxiv.org" in card.get("url", ""):
                    results.append({"title": card["title"], "arxiv_url": card["url"]})
                for lnk in card.get("links", []):
                    if "arxiv.org" in lnk.get("href", ""):
                        results.append({"title": lnk.get("text") or card["title"], "arxiv_url": lnk["href"]})

        # Strategy 3 (concretized): Click "All N versions" to find arxiv
        if not results:
            print("  No arxiv in cards, checking 'All versions'...")
            all_versions_url = page.evaluate("""() => {
                const links = document.querySelectorAll('a');
                for (const a of links) {
                    const text = (a.textContent || "").trim();
                    if (/all\\s+\\d+\\s+versions/i.test(text) || text === 'All versions') {
                        return a.href;
                    }
                }
                return null;
            }""")

            if all_versions_url:
                print(f"  Navigating to All versions: {all_versions_url}")
                page.goto(all_versions_url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(3000)

                # Check for arxiv links on the versions page
                version_links = page.eval_on_selector_all(
                    'a',
                    'els => els.map(e => ({href: e.href, text: (e.textContent || "").trim().substring(0, 120)}))'
                )
                for link in version_links:
                    if "arxiv.org" in link.get("href", ""):
                        results.append({"title": link.get("text", "Arxiv Link"), "arxiv_url": link["href"]})

                # Also check result cards on versions page
                if not results:
                    version_cards = page.evaluate("""() => {
                        const results = [];
                        const cards = document.querySelectorAll('.gs_r.gs_or.gs_scl, .gs_ri, .gs_r');
                        for (const card of cards) {
                            const titleEl = card.querySelector('h3 a, .gs_rt a');
                            if (!titleEl) continue;
                            results.push({ title: (titleEl.textContent || "").trim(), url: titleEl.href });
                        }
                        return results;
                    }""")
                    for card in version_cards:
                        if "arxiv.org" in card.get("url", ""):
                            results.append({"title": card["title"], "arxiv_url": card["url"]})

        # Strategy 4: Regex fallback on page HTML for arxiv URLs
        if not results:
            arxiv_pattern = r'https?://arxiv\.org/(?:abs|pdf)/[\w.]+(?:v\d+)?'
            for m in re.finditer(arxiv_pattern, page.content()):
                url = m.group(0)
                if url not in [r["arxiv_url"] for r in results]:
                    results.append({"title": "Arxiv Link", "arxiv_url": url})
                    if len(results) >= request.max_results:
                        break

        # Deduplicate by URL
        seen = set()
        unique = []
        for r in results:
            if r["arxiv_url"] not in seen:
                seen.add(r["arxiv_url"])
                unique.append(r)
        results = unique[:request.max_results]

        # ── Print results ─────────────────────────────────────────────────
        if results:
            print(f"\nDONE – Found {len(results)} Arxiv link(s):")
            for i, r in enumerate(results, 1):
                print(f"  {i}. {r['title']}")
                print(f"     {r['arxiv_url']}")
        else:
            print("\n❌ No Arxiv links found for this paper.")

    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

    return ScholarPaperSearchResult(
        paper_title=request.paper_title,
        author=request.author,
        links=[ScholarArxivLink(title=r["title"], arxiv_url=r["arxiv_url"]) for r in results],
    )


def test_scholar_paper_search():
    request = ScholarPaperSearchRequest(
        paper_title="nikolaj z3",
        author="",
    )
    port = get_free_port()
    profile_dir = tempfile.mkdtemp(prefix="chrome_cdp_")
    chrome = os.environ.get("CHROME_PATH") or find_chrome_executable()
    chrome_proc = subprocess.Popen(
        [
            chrome,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={profile_dir}",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1280,987",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    ws_url = None
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            resp = urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2)
            ws_url = json.loads(resp.read()).get("webSocketDebuggerUrl", "")
            if ws_url:
                break
        except Exception:
            pass
        time.sleep(0.4)
    if not ws_url:
        raise TimeoutError("Chrome CDP not ready")
    with sync_playwright() as pl:
        browser = pl.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = find_arxiv_links_for_paper(page, request)
        finally:
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)
    print(f"\nFound {len(result.links)} Arxiv links")
    for link in result.links:
        print(f"  {link.arxiv_url}")


if __name__ == "__main__":
    test_scholar_paper_search()
