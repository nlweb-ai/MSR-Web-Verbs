import os
import sys
import json
# Add verbs directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "verbs"))
from amazon_com.amazon_search import search_amazon_products, AmazonSearchRequest
def automate(page):
    # Task refinement: the previous round found 5 Amazon CoQ10 results.
    # The new task asks to search more thoroughly with query "coq10" (exact keyword
    # the user specified) and retrieve 15 items to broaden the price/brand comparison.
    query = "coq10"
    # Search Amazon for 15 CoQ10 products using the exact query the user specified.
    amazon_result = search_amazon_products(
        page,
        AmazonSearchRequest(query=query, max_results=15)
    )
    result = {
        "query": query,
        "date": "2026-03-25",
        "amazon": {
            "products": [
                {"name": p.name, "price": p.price, "rating": p.rating}
                for p in amazon_result.products
            ]
        }
    }
    # Append newly-obtained knowledge to known_facts.md
    facts_path = os.path.join(os.path.dirname(__file__), "known_facts.md")
    with open(facts_path, "a", encoding="utf-8") as f:
        f.write("\n## Amazon CoQ10 Extended Search – 15 Results (as of 2026-03-25)\n\n")
        f.write("### Amazon (query: \"coq10\", 15 items)\n")
        for p in result["amazon"]["products"]:
            f.write(f"- **{p['name']}** — {p['price']} (rating: {p['rating']})\n")
        f.write("\n---\n")
        f.write(f"\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```\n")
    return result