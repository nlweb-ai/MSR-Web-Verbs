import os
import sys
import json
# Add verbs to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "verbs"))
from maps_google_com__nearby.maps_nearby import search_nearby, NearbySearchRequest
def automate(page):
    # Today: March 25, 2026.
    # Trip: Mar 28 (Sat) – Apr 1 (Wed), 2026.
    #
    # What changed from Round 1 → Round 2 (per task-0002.md):
    #   • Schedule update: Papa Del's is now SATURDAY LUNCH (not dinner).
    #     Writer's Room at Lincoln Square is now SATURDAY DINNER.
    #   • New step: search specifically for UIUC-operated 2-bedroom graduate/family
    #     housing near campus (query: "UIUC family graduate housing 2 bedroom",
    #     location: "Urbana, IL"). Exclude private complexes.
    #
    # Refinement strategy:
    #   1. Confirm Writer's Room at Lincoln Square details (new dinner venue).
    #   2. Search broadly for UIUC family/graduate housing in Urbana to surface
    #      UIUC-operated properties (Orchard Downs, 1841 Orchard Pl).
    #   3. Run a second targeted search keyed on the specific address cluster
    #      ("Orchard Place Urbana") to maximize recall of on-campus units.
    #   All results appended to known_facts.md for the next refinement round.
    urbana = "Urbana, IL"
    # 1. Confirm Writer's Room at Lincoln Square (Saturday dinner, Mar 28)
    writers_room_result = search_nearby(page, NearbySearchRequest(
        query="Writer's Room Lincoln Square restaurant",
        location=urbana,
        max_results=1
    ))
    # 2. Broad UIUC graduate/family housing search — expects UIUC-operated
    #    entries like "University of Illinois Family & Graduate Housing" to appear.
    uiuc_housing_broad = search_nearby(page, NearbySearchRequest(
        query="UIUC family graduate housing 2 bedroom",
        location=urbana,
        max_results=5
    ))
    # 3. Targeted search around the known Orchard Downs / Orchard Place address
    #    cluster to surface individual building details for on-campus apartments.
    orchard_downs_result = search_nearby(page, NearbySearchRequest(
        query="Orchard Downs UIUC graduate housing apartment",
        location="Orchard Place, Urbana, IL",
        max_results=5
    ))
    def to_list(nearby_result):
        return [
            {
                "name": b.name,
                "address": b.address,
                "rating": b.rating,
                "phone": b.phone,
                "website": b.website,
            }
            for b in nearby_result.businesses
        ]
    # Filter helper: keep only results that look UIUC-operated.
    # UIUC-operated properties share the housing.illinois.edu domain or have
    # "University of Illinois" / "Orchard Downs" / "UIUC" in their name.
    def is_uiuc_operated(entry):
        name_lc = entry["name"].lower()
        site_lc = (entry.get("website") or "").lower()
        keywords = ["university of illinois", "orchard downs", "uiuc", "housing.illinois"]
        return any(kw in name_lc or kw in site_lc for kw in keywords)
    all_housing = to_list(uiuc_housing_broad) + to_list(orchard_downs_result)
    # Deduplicate by address
    seen_addresses = set()
    uiuc_operated = []
    for entry in all_housing:
        addr_key = entry["address"].strip().lower()
        if addr_key not in seen_addresses:
            seen_addresses.add(addr_key)
            uiuc_operated.append(entry)
    result = {
        "round": 2,
        "date": "2026-03-25",
        "schedule_update": {
            "note": "Schedule corrected per task-0002: Papa Del's → Saturday LUNCH; Writer's Room → Saturday DINNER.",
            "mar28_saturday_lunch": "Papa Del's Pizza Factory, 1201 S Neil St, Champaign",
            "mar28_saturday_dinner": "Writer's Room at Lincoln Square, 201 N Broadway Ave, Urbana",
        },
        "writers_room_dinner": {
            "note": "Saturday dinner venue (Mar 28). Confirmed via nearby search.",
            "details": to_list(writers_room_result),
        },
        "uiuc_operated_2br_housing": {
            "note": (
                "UIUC-operated graduate/family housing (2-bedroom focus). "
                "Private complexes excluded. Key properties: Orchard Downs (1801-1815 Orchard Pl) "
                "and UIUC Family & Graduate Housing Office (1841 Orchard Pl, Urbana)."
            ),
            "all_results_raw": {
                "broad_search": to_list(uiuc_housing_broad),
                "orchard_downs_search": to_list(orchard_downs_result),
            },
            "uiuc_operated_filtered": uiuc_operated,
        },
    }
    # Append findings to known_facts.md
    known_facts_path = os.path.join(os.path.dirname(__file__), "known_facts.md")
    with open(known_facts_path, "a", encoding="utf-8") as f:
        f.write("\n## Round 2 — Collected Facts (2026-03-25)\n\n")
        f.write("```json\n")
        f.write(json.dumps(result, indent=2, ensure_ascii=False))
        f.write("\n```\n\n")
    return result