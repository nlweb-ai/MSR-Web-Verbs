"""
HuggingFace – Search for coding models with Safetensors under a given parameter threshold.
Pure Playwright – no AI.
"""
import re, os, sys, traceback
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class HuggingFaceSearchRequest:
    query: str = "code"
    max_param_billions: float = 9.0
    max_results: int = 5


@dataclass(frozen=True)
class HuggingFaceModel:
    model_name: str
    parameters: str


@dataclass(frozen=True)
class HuggingFaceSearchResult:
    query: str
    max_param_billions: float
    models: list


# Search HuggingFace for coding models that have a Safetensors section and whose
# parameter count (as reported on the model page) is strictly under the given
# threshold.  Returns up to ``max_results`` qualifying models, each with its
# name and parameter count string (e.g. "7B").
def search_huggingface_models(page: Page, request: HuggingFaceSearchRequest) -> HuggingFaceSearchResult:
    collected: list[dict] = []

    try:
        query_encoded = request.query.replace(" ", "+")
        url = f"https://huggingface.co/models?sort=trending&search={query_encoded}"
        print(f"STEP 1: Navigate to HuggingFace models search for '{request.query}'...")
        checkpoint(f"Navigate to HuggingFace models: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(5000)

        # Dismiss cookie/popup banners
        for sel in ["button:has-text('Accept')", "button:has-text('Got it')", "button:has-text('Close')"]:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=500):
                    checkpoint(f"Dismiss popup: {sel}")
                    el.evaluate("el => el.click()")
                    page.wait_for_timeout(400)
            except Exception:
                pass
        page.wait_for_timeout(1000)

        print("STEP 2: Collect model links from search results...")
        checkpoint("Collect model links from search results")
        model_links = page.locator("a[href*='/'][class*=''],  article a, h4 a").all()
        candidates: list[dict] = []
        seen: set[str] = set()
        for link in model_links:
            try:
                href = link.get_attribute("href")
                raw_text = link.inner_text(timeout=2000).strip()
                # Take only the first non-empty line (rest is metadata like tags/stats)
                text = next((l.strip() for l in raw_text.splitlines() if l.strip()), "")
                if (
                    href
                    and "/" in href
                    and not href.startswith("http")
                    and href.count("/") >= 1
                    and len(text) > 2
                    and text not in seen
                    and ("code" in text.lower() or "coder" in text.lower()
                         or "starcoder" in text.lower() or "deepseek" in text.lower())
                ):
                    seen.add(text)
                    candidates.append({"name": text, "href": href})
            except Exception:
                pass
            if len(candidates) >= 15:
                break

        print(f"  Found {len(candidates)} candidate model links")

        print("STEP 3: Visit each model page to check Safetensor section...")
        for cand in candidates:
            if len(collected) >= request.max_results:
                break
            model_name = cand["name"]
            model_url = "https://huggingface.co" + cand["href"]
            print(f"  Checking: {model_name}")
            checkpoint(f"Visit model page: {model_name}")
            try:
                page.goto(model_url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(3000)

                body_text = page.locator("body").inner_text(timeout=10000)

                # Check if Safetensor section exists
                if "safetensor" not in body_text.lower():
                    print(f"    No Safetensor section found, skipping")
                    continue

                # Look for parameter count in the page text
                param_match = None
                for line in body_text.split("\n"):
                    line_lower = line.lower().strip()
                    m = re.search(r"(\d+\.?\d*)\s*[Bb](?:\s|$|\s*param)", line_lower)
                    if m:
                        val = float(m.group(1))
                        if val < request.max_param_billions:
                            param_match = f"{m.group(1)}B"
                            break

                if param_match:
                    collected.append({"model_name": model_name, "parameters": param_match})
                    print(f"    ✓ {model_name} — {param_match} (under {request.max_param_billions}B, has Safetensors)")
                else:
                    print(f"    Parameters not under {request.max_param_billions}B or not found, skipping")

            except Exception as e:
                print(f"    Error: {e}")
                continue

            page.wait_for_timeout(1000)

        print(f"\nDONE – Models found ({len(collected)}):")
        for i, m in enumerate(collected, 1):
            print(f"  {i}. {m['model_name']} | {m['parameters']}")

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

    return HuggingFaceSearchResult(
        query=request.query,
        max_param_billions=request.max_param_billions,
        models=[HuggingFaceModel(model_name=m["model_name"], parameters=m["parameters"]) for m in collected],
    )


def test_huggingface_models() -> None:
    request = HuggingFaceSearchRequest(query="code", max_param_billions=9.0, max_results=5)
    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default",
    )
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir,
            channel="chrome",
            headless=False,
            viewport=None,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--disable-extensions",
            ],
        )
        page = context.pages[0] if context.pages else context.new_page()
        try:
            result = search_huggingface_models(page, request)
            print(f"\nTotal models: {len(result.models)}")
            for i, m in enumerate(result.models, 1):
                print(f"  {i}. {m.model_name} | {m.parameters}")
        finally:
            context.close()


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_huggingface_models)
