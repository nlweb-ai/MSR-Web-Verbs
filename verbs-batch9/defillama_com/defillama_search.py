"""
Auto-generated Playwright script (Python)
DefiLlama – Browse top DeFi protocols by total value locked
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class DefillamaSearchRequest:
    max_results: int = 10


@dataclass
class DefillamaProtocolItem:
    rank: str = ""
    protocol_name: str = ""
    chain: str = ""
    tvl: str = ""
    change_1d: str = ""
    change_7d: str = ""
    mcap_tvl_ratio: str = ""
    category: str = ""


@dataclass
class DefillamaSearchResult:
    items: List[DefillamaProtocolItem] = field(default_factory=list)


# Browse top DeFi protocols by total value locked on DefiLlama.
def defillama_search(page: Page, request: DefillamaSearchRequest) -> DefillamaSearchResult:
    """Browse top DeFi protocols by total value locked on DefiLlama."""
    print(f"  Max results: {request.max_results}\n")

    url = "https://defillama.com/"
    print(f"Loading {url}...")
    checkpoint("Navigate to DefiLlama homepage")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(8000)

    result = DefillamaSearchResult()

    checkpoint("Extract protocol listings from TVL table")
    js_code = """(max) => {
        const items = [];
        const rows = document.querySelectorAll('.vf-row');
        for (let r = 0; r < rows.length && items.length < max; r++) {
            const cells = rows[r].children;
            if (cells.length < 5) continue;
            // cell 0: "Bookmark | Name | X chains"
            const nameLines = cells[0].innerText.split('\\n').map(l => l.trim()).filter(l => l && l !== 'Bookmark' && !l.match(/^Hide child/));
            const name = nameLines[0] || '';
            const chains = nameLines[1] || '';
            if (!name || name.length < 2) continue;
            const category = (cells[1] || {}).innerText?.trim() || '';
            const tvl = (cells[2] || {}).innerText?.trim() || '';
            const change1d = (cells[3] || {}).innerText?.trim() || '';
            const change7d = (cells[4] || {}).innerText?.trim() || '';
            const mcapTvl = (cells[8] || {}).innerText?.trim() || '';
            items.push({
                rank: String(r + 1),
                protocol_name: name,
                chain: chains,
                tvl: tvl,
                change_1d: change1d,
                change_7d: change7d,
                mcap_tvl_ratio: mcapTvl,
                category: category
            });
        }
        return items;
    }"""
    items_data = page.evaluate(js_code, request.max_results)

    for d in items_data:
        item = DefillamaProtocolItem()
        item.rank = d.get("rank", "")
        item.protocol_name = d.get("protocol_name", "")
        item.chain = d.get("chain", "")
        item.tvl = d.get("tvl", "")
        item.change_1d = d.get("change_1d", "")
        item.change_7d = d.get("change_7d", "")
        item.mcap_tvl_ratio = d.get("mcap_tvl_ratio", "")
        item.category = d.get("category", "")
        result.items.append(item)

    for i, item in enumerate(result.items, 1):
        print(f"\n  Protocol {i}:")
        print(f"    Rank:         {item.rank}")
        print(f"    Name:         {item.protocol_name}")
        print(f"    Chain:        {item.chain}")
        print(f"    TVL:          {item.tvl}")
        print(f"    1d Change:    {item.change_1d}")
        print(f"    7d Change:    {item.change_7d}")
        print(f"    Mcap/TVL:     {item.mcap_tvl_ratio}")
        print(f"    Category:     {item.category}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("defillama")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            request = DefillamaSearchRequest()
            result = defillama_search(page, request)
            print("\n=== DONE ===")
            print(f"Found {len(result.items)} protocols")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
