import os
import sys
import json
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "verbs"))
from amazon_com.amazon_search import search_amazon_products, AmazonSearchRequest
def parse_dosage_mg(name):
    """Extract dosage in mg from product name string."""
    match = re.search(r'(\d+)\s*mg', name, re.IGNORECASE)
    return int(match.group(1)) if match else None
def parse_count(name):
    """Extract pill/softgel count from product name string."""
    match = re.search(r'(\d+)\s*(ct|count|softgels?|capsules?|gummies|tablets?)', name, re.IGNORECASE)
    return int(match.group(1)) if match else None
def parse_price_float(price_str):
    """Parse price string like '$36.99' to a float."""
    match = re.search(r'[\d.]+', price_str.replace(',', ''))
    return float(match.group()) if match else None
def automate(page):
    # Task-0002 asks to expand the Amazon CoQ10 search:
    # use query "CoQ10 supplement" and retrieve up to 10 results,
    # then compare by dosage (mg) and per-count cost for value analysis.
    # Known facts show Amazon has the lowest per-count price for Qunol Ultra 100mg (~$0.23/ct),
    # so we want to surface more options and rank by $/ct to confirm or find better value.
    query = "CoQ10 supplement"
    max_results = 10
    amazon_result = search_amazon_products(page, AmazonSearchRequest(query=query, max_results=max_results))
    products = []
    for p in amazon_result.products:
        dosage_mg = parse_dosage_mg(p.name)
        count = parse_count(p.name)
        price_float = parse_price_float(p.price)
        # Per-count cost is the most useful value metric across different pack sizes
        if price_float is not None and count and count > 0:
            per_count = round(price_float / count, 4)
        else:
            per_count = None
        products.append({
            "name": p.name,
            "price": p.price,
            "rating": p.rating,
            "dosage_mg": dosage_mg,
            "count": count,
            "per_count_cost": per_count,
        })
    # Sort by per-count cost ascending (best value first); None values pushed to end
    sorted_products = sorted(
        products,
        key=lambda x: (x["per_count_cost"] is None, x["per_count_cost"] or 9999)
    )
    result = {
        "query": query,
        "summary": "Expanded Amazon CoQ10 search with dosage and per-count cost analysis (up to 10 results)",
        "products": sorted_products,
        "best_value": sorted_products[0] if sorted_products else None,
    }
    # Append new findings to known_facts.md
    facts_path = os.path.join(os.path.dirname(__file__), "known_facts.md")
    with open(facts_path, "a", encoding="utf-8") as f:
        f.write("\n\n## Expanded Amazon CoQ10 Search (2026-03-25)\n\n")
        f.write("| Product | Price | Rating | Dosage | Count | $/ct |\n")
        f.write("|---------|-------|--------|--------|-------|------|\n")
        for p in sorted_products:
            dosage = f"{p['dosage_mg']}mg" if p['dosage_mg'] else "N/A"
            count_str = str(p['count']) if p['count'] else "N/A"
            per_ct = f"${p['per_count_cost']:.4f}" if p['per_count_cost'] is not None else "N/A"
            name_truncated = p['name'][:60] + ("..." if len(p['name']) > 60 else "")
            f.write(f"| {name_truncated} | {p['price']} | {p['rating']} | {dosage} | {count_str} | {per_ct} |\n")
        if result["best_value"]:
            bv = result["best_value"]
            per_ct_str = f"${bv['per_count_cost']:.4f}/ct" if bv['per_count_cost'] is not None else "N/A"
            f.write(
                f"\n**Best value on Amazon**: {bv['name']} | {bv['price']} | "
                f"{bv['dosage_mg']}mg × {bv['count']}ct = {per_ct_str}\n"
            )
        f.write("\n```json\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n```\n")
    return result