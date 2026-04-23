"""
OpenSecrets – Lobbying Issue Search

Search OpenSecrets lobbying data by issue area and extract the top lobbying
clients: name, subsidiary, and number of reports.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws

# Issue code mapping for common topics
ISSUE_CODES = {
    "technology": "SCI",
    "healthcare": "HCR",
    "defense": "DEF",
    "energy": "ENG",
    "environment": "ENV",
    "taxes": "TAX",
    "trade": "TRD",
}


@dataclass(frozen=True)
class Request:
    Topic: str = "technology"
    num_results: int = 5


@dataclass
class LobbyingClient:
    name: str = ""
    subsidiary: str = ""
    num_reports: str = ""


@dataclass
class Result:
    issue_area: str = ""
    total_clients: str = ""
    total_reports: str = ""
    clients: List[LobbyingClient] = field(default_factory=list)


def lobbying_search(page, request: Request) -> Result:
    """Search OpenSecrets for lobbying data by issue area."""

    issue_code = ISSUE_CODES.get(request.Topic.lower(), "SCI")
    url = f"https://www.opensecrets.org/federal-lobbying/issues/summary?id={issue_code}&cycle=2024"
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    data = page.evaluate(r"""(numResults) => {
        // Extract issue area name from page title
        const titleMatch = document.title.match(/^(.+?)Lobbying/);
        const issueArea = titleMatch ? titleMatch[1].trim() : document.title;

        // Extract summary stats from body text
        const bodyText = document.body.innerText;
        const clientsMatch = bodyText.match(/(\d[\d,]*)\s*\nTotal Number of Clients/);
        const reportsMatch = bodyText.match(/(\d[\d,]*)\s*\nNumber of Reports/);
        const totalClients = clientsMatch ? clientsMatch[1] : '';
        const totalReports = reportsMatch ? reportsMatch[1] : '';

        // Extract table rows
        const table = document.querySelector('table');
        if (!table) return { issueArea, totalClients, totalReports, clients: [] };

        const rows = Array.from(table.rows).slice(1, 1 + numResults);
        const clients = rows.map(row => {
            const cells = Array.from(row.cells).map(c => c.textContent.trim());
            return {
                name: cells[0] || '',
                subsidiary: cells[1] || '-',
                numReports: cells[2] || '',
            };
        });

        return { issueArea, totalClients, totalReports, clients };
    }""", request.num_results)

    return Result(
        issue_area=data.get("issueArea", ""),
        total_clients=data.get("totalClients", ""),
        total_reports=data.get("totalReports", ""),
        clients=[
            LobbyingClient(
                name=c.get("name", ""),
                subsidiary=c.get("subsidiary", ""),
                num_reports=c.get("numReports", ""),
            )
            for c in data.get("clients", [])
        ],
    )


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("opensecrets_lobbying")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            req = Request(Topic="technology", num_results=5)
            result = lobbying_search(page, req)
            print(f"\nIssue Area: {result.issue_area}")
            print(f"Total Clients: {result.total_clients}")
            print(f"Total Reports: {result.total_reports}")
            print(f"\nTop {len(result.clients)} Lobbying Clients:")
            for i, c in enumerate(result.clients, 1):
                sub = f" (via {c.subsidiary})" if c.subsidiary and c.subsidiary != "-" else ""
                print(f"  {i}. {c.name}{sub} — {c.num_reports} reports")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
