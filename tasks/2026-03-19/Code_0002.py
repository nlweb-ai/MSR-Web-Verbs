"""
Code_0002.py — Round 2 refinement for UIUC visit, March 28–April 1, 2026.
Changes vs. Round 1 (Code_0001.py):
  1. Papa Del's → LUNCH (Sat Mar 28).
     User explicitly requested the meal be moved to lunch. Deep-dish pizza at
     lunch is perfectly reasonable, and it frees the evening for a lighter
     OpenTable dinner option.
  2. Saturday DINNER is now TBD → OpenTable search (2 covers, Champaign, IL).
  3. NEW: Google Maps saved list — University Housing Tour.
     Creates a list named "UIUC Housing Tour" with the seven AC traditional
     halls the user wants to visit in person:
     Allen, Busey, Evans, Oglesby, Trelease, Wardall, Weston.
  4. NEW: Google Maps saved list — Chinese Restaurants.
     Bundles Chinatown Buffet (fixed) + the five 4.9★ options already
     surfaced in Round 1 into one saved list so navigation is one tap away.
"""
import os
import sys
import json
import dataclasses
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "verbs"))
from playwright.sync_api import sync_playwright
from maps_google_com__nearby.maps_nearby import search_nearby, NearbySearchRequest
from opentable_com.opentable_search import search_opentable_restaurants, OpentableSearchRequest
from maps_google_com__createList.maps_createList import create_saved_list, CreateListRequest
def automate(page):
    # ------------------------------------------------------------------
    # 1. Papa Del's details — now confirmed as SATURDAY LUNCH (Mar 28)
    # ------------------------------------------------------------------
    # User requested the meal be moved to lunch. We still fetch its details
    # (address, rating, phone) via Google Maps nearby for the known_facts record.
    papa_dels_result = search_nearby(page, NearbySearchRequest(
        query="Papa Del's Pizza",
        location="Champaign, IL",
        max_results=1
    ))
    # ------------------------------------------------------------------
    # 2. Saturday DINNER candidates via OpenTable (Sat Mar 28, 2 covers)
    # ------------------------------------------------------------------
    # Lunch is now Papa Del's, so we search OpenTable for a dinner option
    # for Shuo & Ashley. Surface up to 5 candidates so they can choose.
    dinner_result = search_opentable_restaurants(page, OpentableSearchRequest(
        location="Champaign, IL",
        covers=2,
        max_results=5
    ))
    # ------------------------------------------------------------------
    # 3. Create Google Maps list — University Housing Tour
    # ------------------------------------------------------------------
    # The seven AC traditional halls specified in task-0002 for in-person
    # touring. We suffix each with "UIUC" to help Maps find the right place.
    housing_halls = [
        "Allen Hall UIUC",
        "Busey Hall UIUC",
        "Evans Hall UIUC",
        "Oglesby Hall UIUC",
        "Trelease Hall UIUC",
        "Wardall Hall UIUC",
        "Weston Hall UIUC",
    ]
    housing_list_result = create_saved_list(page, CreateListRequest(
        list_name="UIUC Housing Tour",
        places=housing_halls
    ))
    # ------------------------------------------------------------------
    # 4. Create Google Maps list — Chinese Restaurants
    # ------------------------------------------------------------------
    # Consolidates Chinatown Buffet (fixed visit) and the five 4.9★ options
    # surfaced in Round 1 into a single navigable saved list.
    chinese_places = [
        "Chinatown Buffet Champaign IL",
        "Northern Cuisine 404 E Green St Champaign",
        "Golden Harbor 505 S Neil St Champaign",
        "Dimsum House 402 E Green St Champaign",
        "Peking Garden 206 N Randolph St Champaign",
        "Cravings 603 S Wright St Champaign",
    ]
    chinese_list_result = create_saved_list(page, CreateListRequest(
        list_name="Champaign Chinese Restaurants",
        places=chinese_places
    ))
    # ------------------------------------------------------------------
    # Assemble result JSON (newly obtained knowledge for this round)
    # ------------------------------------------------------------------
    result = {
        "visit_week": "March 28 – April 1, 2026",
        "concretization_date": "2026-03-22",
        "round": 2,
        "changes_from_round_1": [
            "Papa Del's moved from dinner to lunch on Sat Mar 28",
            "Saturday dinner is now TBD — OpenTable candidates provided",
            "Created Google Maps saved list for housing halls tour",
            "Created Google Maps saved list for Chinese restaurants",
        ],
        "saturday_mar28": {
            # Papa Del's is now LUNCH
            "lunch_at_papa_dels": {
                "note": "Papa Del's confirmed as Saturday lunch (user requested change from dinner).",
                "details": [dataclasses.asdict(b) for b in papa_dels_result.businesses],
            },
            # Dinner is now the open slot
            "dinner_candidates_via_opentable": [
                {
                    "name": r.name,
                    "cuisine": r.cuisine,
                    "rating": r.rating,
                    "available_times": r.available_times,
                }
                for r in dinner_result.restaurants
            ],
        },
        "sun_to_tue_mar29_31": {
            "housing_tour_map_list": {
                "note": "Google Maps saved list for the seven AC traditional halls to tour in person.",
                "saved_list_name": housing_list_result.list_name,
                "places_added": housing_list_result.places_added,
                "all_saved": housing_list_result.success,
            },
        },
        "chinese_restaurants_map_list": {
            "note": "Google Maps saved list covering Chinatown Buffet + five 4.9★ options.",
            "saved_list_name": chinese_list_result.list_name,
            "places_added": chinese_list_result.places_added,
            "all_saved": chinese_list_result.success,
        },
    }
    # Append collected knowledge to known_facts.md
    known_facts_path = os.path.join(
        os.path.dirname(__file__), "known_facts.md"
    )
    with open(known_facts_path, "a", encoding="utf-8") as f:
        f.write("\n\n## Round 2 — collected 2026-03-22\n\n```json\n")
        f.write(json.dumps(result, indent=2, ensure_ascii=False))
        f.write("\n```\n")
    return result
def main():
    user_data_dir = os.path.join(
        os.environ["USERPROFILE"],
        "AppData", "Local", "Google", "Chrome", "User Data", "Default"
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
            result = automate(page)
            print("Final output:", json.dumps(result, indent=2, ensure_ascii=False))
        finally:
            context.close()
if __name__ == "__main__":
    main()