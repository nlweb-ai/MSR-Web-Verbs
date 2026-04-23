import re
import os
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page

import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
from playwright_debugger import checkpoint

@dataclass(frozen=True)
class EtherscanAddressRequest:
    address: str = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    max_transactions: int = 5

@dataclass(frozen=True)
class EthTransaction:
    hash: str = ""
    from_addr: str = ""
    to_addr: str = ""
    value: str = ""
    timestamp: str = ""

@dataclass(frozen=True)
class EtherscanAddressResult:
    address: str = ""
    eth_balance: str = ""
    usd_value: str = ""
    transactions: list = None  # list[EthTransaction]

# Navigate to Etherscan.io and look up an Ethereum address to extract
# ETH balance, USD value, and recent transactions with details.
def etherscan_address(page: Page, request: EtherscanAddressRequest) -> EtherscanAddressResult:
    address = request.address
    max_transactions = request.max_transactions
    print(f"  Address: {address}\n")

    url = f"https://etherscan.io/address/{address}"
    print(f"Loading {url}...")
    checkpoint(f"Navigate to {url}")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    print(f"  Loaded: {page.url}")

    text = page.evaluate("document.body ? document.body.innerText : ''") or ""
    text_lines = [l.strip() for l in text.split("\n") if l.strip()]

    # --- Extract ETH balance ---
    eth_balance = "N/A"
    for line in text_lines:
        m = re.search(r'([\d,.]+)\s*Ether', line, re.I)
        if m:
            eth_balance = m.group(0).strip()
            break

    # --- Extract USD value ---
    usd_value = "N/A"
    for line in text_lines:
        m = re.search(r'\$[\d,.]+', line)
        if m:
            usd_value = m.group(0).strip()
            break

    print(f"  ETH Balance: {eth_balance}")
    print(f"  USD Value:   {usd_value}")

    # --- Extract transactions from the transaction table ---
    transactions = []

    # Look for transaction hashes (0x..., 64 hex chars) in page text
    tx_hashes = []
    for line in text_lines:
        hm = re.findall(r'0x[0-9a-fA-F]{64}', line)
        tx_hashes.extend(hm)

    # If no full hashes found, look for abbreviated hashes (0xAbCd...1234)
    if not tx_hashes:
        for line in text_lines:
            hm = re.findall(r'0x[0-9a-fA-F]{4,}\.{2,3}[0-9a-fA-F]{4,}', line)
            tx_hashes.extend(hm)

    # De-duplicate while preserving order
    seen = set()
    unique_hashes = []
    for h in tx_hashes:
        if h not in seen:
            seen.add(h)
            unique_hashes.append(h)
    tx_hashes = unique_hashes[:max_transactions]

    # Try to extract transaction rows from the table
    # Etherscan transaction table typically shows:
    # Transaction Hash | Method | Block | Age | From | To | Value | Txn Fee
    # We'll try to parse rows around each tx hash
    for tx_hash in tx_hashes:
        from_addr = "N/A"
        to_addr = "N/A"
        value = "N/A"
        timestamp = "N/A"

        # Find the line index containing this tx hash
        hash_idx = None
        for i, line in enumerate(text_lines):
            if tx_hash in line:
                hash_idx = i
                break

        if hash_idx is not None:
            # Look in surrounding lines for addresses, values, and timestamps
            window = text_lines[max(0, hash_idx - 2):min(len(text_lines), hash_idx + 10)]
            for wline in window:
                # From/To addresses (0x... 40 hex chars, or abbreviated)
                addr_matches = re.findall(r'0x[0-9a-fA-F]{40}', wline)
                if not addr_matches:
                    addr_matches = re.findall(r'0x[0-9a-fA-F]{4,}\.{2,3}[0-9a-fA-F]{4,}', wline)

                if addr_matches:
                    for am in addr_matches:
                        if am == tx_hash:
                            continue
                        if from_addr == "N/A":
                            from_addr = am
                        elif to_addr == "N/A":
                            to_addr = am

                # ETH value
                vm = re.search(r'([\d,.]+)\s*ETH', wline, re.I)
                if vm and value == "N/A":
                    value = vm.group(0).strip()

                # Timestamp (e.g., "2 hrs ago", "5 days ago", or date format)
                tm = re.search(r'(\d+\s+(?:sec|min|hr|hour|day|week|month|yr|year)s?\s+ago)', wline, re.I)
                if tm and timestamp == "N/A":
                    timestamp = tm.group(1).strip()
                if timestamp == "N/A":
                    dm = re.search(r'(\d{4}-\d{2}-\d{2})', wline)
                    if dm:
                        timestamp = dm.group(1)

        transactions.append(EthTransaction(
            hash=tx_hash,
            from_addr=from_addr,
            to_addr=to_addr,
            value=value,
            timestamp=timestamp,
        ))

    print("=" * 60)
    print(f"Etherscan Address: {address}")
    print("=" * 60)
    print(f"  ETH Balance: {eth_balance}")
    print(f"  USD Value:   {usd_value}")
    print(f"\n  Recent Transactions ({len(transactions)}):")
    for idx, tx in enumerate(transactions, 1):
        print(f"    {idx}. {tx.hash}")
        print(f"       From: {tx.from_addr}")
        print(f"       To:   {tx.to_addr}")
        print(f"       Value: {tx.value}")
        print(f"       Time:  {tx.timestamp}")

    return EtherscanAddressResult(
        address=address,
        eth_balance=eth_balance,
        usd_value=usd_value,
        transactions=transactions,
    )

def test_func():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.new_page()
        result = etherscan_address(page, EtherscanAddressRequest())
        for tx in (result.transactions or []):
            print(f"  {tx.hash} | {tx.value}")
        browser.close()

if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)
