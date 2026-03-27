"""
WebMD – Search for symptoms and extract conditions.
Uses the main search functionality, no hardcoded symptom URLs.
Pure Playwright with temp profile.
"""
import re
import os
import shutil
import tempfile
import traceback
from playwright.sync_api import Page, sync_playwright

import sys as _sys, os as _os, shutil
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), '..'))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws, find_chrome_executable
from playwright_debugger import checkpoint
from dataclasses import dataclass
import subprocess
import json
import time
from urllib.request import urlopen


@dataclass(frozen=True)
class WebMDSearchRequest:
    symptom: str = "headache"
    max_results: int = 5


@dataclass(frozen=True)
class WebMDCondition:
    condition: str
    url: str


@dataclass(frozen=True)
class WebMDSearchResult:
    symptom: str
    conditions: list


def search_webmd_conditions(page: Page, request: WebMDSearchRequest) -> WebMDSearchResult:
    """Search WebMD for a symptom and extract related conditions."""
    conditions = []

    try:
        # STEP 1: Navigate to WebMD
        print("STEP 1: Navigate to WebMD...")
        checkpoint("Navigate to WebMD homepage")
        page.goto("https://www.webmd.com", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)

        # Dismiss cookie/ad popups
        for sel in ["button:has-text('Accept')", "button:has-text('I Accept')",
                    "button:has-text('Got It')", "#onetrust-accept-btn-handler",
                    "[aria-label='Close']", "button:has-text('No Thanks')"]:
            try:
                loc = page.locator(sel).first
                if loc.is_visible(timeout=500):
                    checkpoint("Dismiss popup")
                    loc.evaluate("el => el.click()")
                    page.wait_for_timeout(300)
            except Exception:
                pass

        # STEP 2: Search for the symptom using site search
        print(f"STEP 2: Search for '{request.symptom}'...")
        
        # Try various search input selectors
        search_selectors = [
            "input[name='query']",
            "input[placeholder*='Search']",
            "input[type='search']",
            "#search-input",
            "[data-testid='search-input']",
            "input[aria-label*='search' i]",
        ]
        
        search_input = None
        for sel in search_selectors:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=1000):
                    search_input = el
                    break
            except Exception:
                continue
        
        if search_input:
            checkpoint("Click search input")
            search_input.click()
            page.wait_for_timeout(500)
            checkpoint("Fill search input with symptom")
            search_input.fill(request.symptom)
            page.wait_for_timeout(1000)
            
            # Try to click a suggestion or press Enter
            try:
                # Look for dropdown suggestion
                suggestion = page.locator(f"li:has-text('{request.symptom}'), a:has-text('{request.symptom}'), [role='option']:has-text('{request.symptom}')").first
                if suggestion.is_visible(timeout=1500):
                    checkpoint("Click search suggestion")
                    suggestion.click()
                else:
                    checkpoint("Press Enter to search")
                    search_input.press("Enter")
            except Exception:
                checkpoint("Press Enter to search (fallback)")
                search_input.press("Enter")
            
            page.wait_for_timeout(4000)
            print(f"  Search results: {page.url}")
        else:
            # Fallback: go directly to search results page
            print("  Search input not found, using search URL...")
            checkpoint("Navigate to search results page")
            page.goto(f"https://www.webmd.com/search/search_results/default.aspx?query={request.symptom}",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(4000)

        # STEP 3: Click on a relevant result to get to conditions page
        print("STEP 3: Navigate to conditions page...")
        
        # Look for links related to conditions/symptoms
        result_selectors = [
            "a:has-text('Symptoms')",
            "a:has-text('conditions')",
            f"a:has-text('{request.symptom}')",
            ".search-results a",
            "article a",
        ]
        
        for sel in result_selectors:
            try:
                links = page.locator(sel).all()
                for link in links[:5]:
                    href = link.get_attribute("href") or ""
                    text = link.inner_text(timeout=1000).strip()
                    # Skip nav links
                    if any(x in text.lower() for x in ["sign in", "subscribe", "newsletter"]):
                        continue
                    if request.symptom.lower() in text.lower() and len(text) > 5:
                        checkpoint("Click search result link")
                        link.click()
                        page.wait_for_timeout(4000)
                        print(f"  Clicked: {text[:50]}")
                        break
                else:
                    continue
                break
            except Exception:
                continue

        # Scroll to load content
        for _ in range(5):
            page.evaluate("window.scrollBy(0, 600)")
            page.wait_for_timeout(500)

        # STEP 4: Extract conditions
        print("STEP 4: Extract headache-related conditions...")
        seen = set()
        
        # Strategy 1: Find condition/article links
        links = page.locator("a").all()
        nav_words = {"log in", "sign in", "overview", "symptoms", "causes",
                     "complications", "treatment", "prevention", "diagnosis",
                     "living with", "next steps", "related", "more",
                     "support & resources", "find a doctor", "subscribe",
                     "newsletter", "slideshows", "videos", "quizzes", "home",
                     "health", "drugs", "news", "webmd"}
        
        for link in links:
            if len(conditions) >= request.max_results:
                break
            try:
                text = link.inner_text(timeout=500).strip()
                text = text.splitlines()[0].strip() if text else ""
                href = link.get_attribute("href") or ""
                
                # Filter for condition-like links
                if (text and 15 < len(text) < 120 
                    and request.symptom.lower() in text.lower()
                    and text.lower() not in seen
                    and not any(nw in text.lower() for nw in nav_words)):
                    seen.add(text.lower())
                    full_url = href if href.startswith("http") else f"https://www.webmd.com{href}"
                    conditions.append({"condition": text, "url": full_url})
            except Exception:
                continue

        # Strategy 2: Parse body text for condition-like mentions
        if len(conditions) < request.max_results:
            body_text = page.inner_text("body")
            lines = [l.strip() for l in body_text.splitlines() if l.strip()]
            for line in lines:
                if len(conditions) >= request.max_results:
                    break
                if (request.symptom.lower() in line.lower() 
                    and 15 < len(line) < 150
                    and line.lower() not in seen
                    and not any(nw in line.lower() for nw in nav_words)):
                    seen.add(line.lower())
                    conditions.append({"condition": line, "url": "N/A"})

        # Print results
        print(f"\n{'=' * 59}")
        print(f"  Results – Top {len(conditions)} {request.symptom.title()}-Related Conditions")
        print(f"{'=' * 59}\n")
        
        if conditions:
            for i, c in enumerate(conditions, 1):
                print(f"  {i}. {c['condition']}")
                if c.get('url') and c['url'] != "N/A":
                    print(f"     URL: {c['url'][:80]}")
        else:
            print("  No conditions found.")

    except Exception as e:
        print(f"\nError: {e}")
        traceback.print_exc()
    return WebMDSearchResult(
        symptom=request.symptom,
        conditions=[WebMDCondition(condition=c['condition'], url=c.get('url', 'N/A')) for c in conditions],
    )


def test_webmd_conditions():
    from playwright.sync_api import sync_playwright
    request = WebMDSearchRequest(symptom="headache", max_results=5)
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
            result = search_webmd_conditions(page, request)
        finally:
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)
    print(f"\nSymptom: {result.symptom}")
    print(f"Conditions found: {len(result.conditions)}")
    for i, c in enumerate(result.conditions, 1):
        print(f"  {i}. {c.condition}")
        if c.url != "N/A":
            print(f"     {c.url[:80]}")


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_webmd_conditions)
