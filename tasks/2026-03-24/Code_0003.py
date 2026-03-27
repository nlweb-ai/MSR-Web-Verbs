import os
import sys
import json
# Add verbs directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "verbs"))
from cvs_com.cvs_search import search_cvs_stores, CvsSearchRequest
def automate(page):
    # Refinement strategy:
    # The task asks to find CVS stores in Bellevue, WA.
    # Bellevue, WA has several ZIP codes; 98004 is the central downtown ZIP.
    # We search with max_results=10 to capture all or most locations in/around Bellevue.
    zip_code = "98004"
    request = CvsSearchRequest(zip_code=zip_code, max_results=10)
    cvs_result = search_cvs_stores(page, request)
    result = {
        "query": "CVS stores in Bellevue, WA",
        "date": "2026-03-26",
        "zip_code_searched": zip_code,
        "stores": [
            {
                "address": store.address,
                "phone": store.phone,
                "hours": store.hours,
                "has_pharmacy": store.has_pharmacy,
                "has_minuteclinic": store.has_minuteclinic,
            }
            for store in cvs_result.stores
        ]
    }
    # Append newly-obtained knowledge to known_facts.md
    facts_path = os.path.join(os.path.dirname(__file__), "known_facts.md")
    with open(facts_path, "a", encoding="utf-8") as f:
        f.write("\n## CVS Stores in Bellevue, WA (as of 2026-03-26)\n\n")
        f.write(f"### Search ZIP: {zip_code}\n")
        for store in result["stores"]:
            f.write(f"- **{store['address']}** | Phone: {store['phone']} | Hours: {store['hours']} | Pharmacy: {store['has_pharmacy']} | MinuteClinic: {store['has_minuteclinic']}\n")
        f.write("\n---\n")
        f.write(f"\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```\n")
    return result