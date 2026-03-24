"""
Code_0001.py — Refinement for UIUC visit task, week of March 28–April 1, 2026.
Travel context (DeterminedFacts.md):
  - Shuo & Ashley arrive Champaign Sat Mar 28 (fly SEA→ORD, then drive to Champaign).
  - Sat Mar 28 (together): lunch + dinner; one meal at Papa Del's; campus photo walk.
  - Sun Mar 29 – Tue Mar 31: Ashley at UIUC department events.
  - Sun Mar 29 – Tue Mar 31: Shuo tours car dealerships + university housing.
  - Any day: Chinese restaurants, including one visit to Chinatown Buffet.
Refinement strategy / concretization decisions:
  1. PAPA DEL'S → DINNER on Sat Mar 28.
     Deep-dish pizza is a sit-down evening experience; the pair arrives in the
     morning so breakfast/lunch can be lighter. We use Google Maps nearby to
     confirm the address, rating, and phone number.
  2. SATURDAY LUNCH → OpenTable search in Champaign for 2 covers.
     We surface up to 5 candidates with available times so Shuo can pick on the
     day once they settle into the hotel.
  3. CAMPUS PHOTO LANDMARKS (Sat Mar 28 afternoon).
     Pre-selected eight iconic UIUC spots spanning the main quad, athletics, arts,
     and research — a walkable ~2-mile circuit:
       • Alma Mater Statue       • Foellinger Auditorium
       • Main Quad UIUC          • Illini Union
       • Memorial Stadium        • Natural History Building UIUC
       • Beckman Institute UIUC  • Krannert Art Museum UIUC
     We create a Google Maps saved list so navigation is one tap away.
  4. CAR DEALERSHIPS (Sun–Tue). Google Maps nearby for "car dealership" in
     Champaign IL, max 5 results — real names, addresses, ratings.
  5. UNIVERSITY HOUSING. housing_illinois_edu search: Double room, mid-tier
     meal plan ("Room & 12 Classic Meals + 15 Dining Dollars"), wide price band
     (0–30 000) so all halls are surfaced.
  6. CHINESE RESTAURANTS. Google Maps nearby "Chinese restaurant" in Champaign IL,
     max 5. Chinatown Buffet is pinned as a fixed confirmed choice.
"""
import os
import sys
import json
import dataclasses
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "verbs"))
from playwright.sync_api import sync_playwright
from maps_google_com__nearby.maps_nearby import search_nearby, NearbySearchRequest
from opentable_com.opentable_search import search_opentable_restaurants, OpentableSearchRequest
from housing_illinois_edu.housing_search import search_housing_cost, HousingSearchRequest
from maps_google_com__createList.maps_createList import create_saved_list, CreateListRequest
def automate(page):
    # ------------------------------------------------------------------
    # 1. Papa Del's details — confirmed dinner venue on Sat Mar 28
    # ------------------------------------------------------------------
    # Deep-dish pizza is best as a dinner; the pair arrives from Chicago
    # in the morning so this anchors the evening plan.
    papa_dels_result = search_nearby(page, NearbySearchRequest(
        query="Papa Del's Pizza",
        location="Champaign, IL",
        max_results=1
    ))
    # ------------------------------------------------------------------
    # 2. Saturday lunch candidates via OpenTable (Sat Mar 28, 2 covers)
    # ------------------------------------------------------------------
    # We give up to 5 options so Shuo can choose on the day.
    lunch_result = search_opentable_restaurants(page, OpentableSearchRequest(
        location="Champaign, IL",
        covers=2,
        max_results=5
    ))
    # ------------------------------------------------------------------
    # 3. Save UIUC campus photo landmarks to a Google Maps list
    # ------------------------------------------------------------------
    # Eight iconic spots forming a walkable circuit on and near the main quad.
    campus_landmarks = [
        "Alma Mater Statue UIUC",
        "Foellinger Auditorium UIUC",
        "Main Quad UIUC",
        "Illini Union Champaign",
        "Memorial Stadium Champaign",
        "Natural History Building UIUC",
        "Beckman Institute UIUC",
        "Krannert Art Museum UIUC",
    ]
    landmarks_list_result = create_saved_list(page, CreateListRequest(
        list_name="UIUC Photo Walk Mar 28",
        places=campus_landmarks
    ))
    # ------------------------------------------------------------------
    # 4. Car dealerships near Champaign (Sun Mar 29 – Tue Mar 31)
    # ------------------------------------------------------------------
    dealerships_result = search_nearby(page, NearbySearchRequest(
        query="car dealership",
        location="Champaign, IL",
        max_results=5
    ))
    # ------------------------------------------------------------------
    # 5. UIUC university housing options (Sun Mar 29 – Tue Mar 31)
    # ------------------------------------------------------------------
    # Double room is the most common undergrad configuration.
    # "Room & 12 Classic Meals + 15 Dining Dollars" is a standard mid-tier plan.
    # Wide price range (0–30000) to surface all available halls.
    housing_result = search_housing_cost(page, HousingSearchRequest(
        meal_plan="Room & 12 Classic Meals + 15 Dining Dollars",
        room_type="Double",
        price_min=0,
        price_max=30000
    ))
    # ------------------------------------------------------------------
    # 6. Chinese restaurants near UIUC (any day; Chinatown Buffet is fixed)
    # ------------------------------------------------------------------
    chinese_result = search_nearby(page, NearbySearchRequest(
        query="Chinese restaurant",
        location="Champaign, IL",
        max_results=5
    ))
    # ------------------------------------------------------------------
    # Assemble result JSON
    # ------------------------------------------------------------------
    result = {
        "visit_week": "March 28 – April 1, 2026",
        "concretization_date": "2026-03-22",
        "saturday_mar28": {
            "dinner_at_papa_dels": {
                "note": "Papa Del's chosen for dinner (deep-dish pizza is an evening meal).",
                "details": [dataclasses.asdict(b) for b in papa_dels_result.businesses],
            },
            "lunch_candidates_via_opentable": [
                {
                    "name": r.name,
                    "cuisine": r.cuisine,
                    "rating": r.rating,
                    "available_times": r.available_times,
                }
                for r in lunch_result.restaurants
            ],
            "campus_photo_walk": {
                "note": "Walkable ~2-mile circuit of eight iconic UIUC landmarks.",
                "saved_list_name": landmarks_list_result.list_name,
                "places_added": landmarks_list_result.places_added,
                "all_saved": landmarks_list_result.success,
            },
        },
        "sun_to_tue_mar29_31": {
            "car_dealerships": [
                {
                    "name": b.name,
                    "address": b.address,
                    "rating": b.rating,
                    "phone": b.phone,
                    "website": b.website,
                }
                for b in dealerships_result.businesses
            ],
            "university_housing_options": {
                "room_type": housing_result.room_type,
                "meal_plan": housing_result.meal_plan,
                "halls": [
                    {"hall_name": h.hall_name, "annual_price_usd": h.price}
                    for h in housing_result.halls
                ],
            },
        },
        "chinese_restaurants": {
            "fixed_visit": {
                "name": "Chinatown Buffet",
                "location": "Champaign, IL",
                "note": "Explicitly requested by user for one meal.",
            },
            "additional_options": [
                {
                    "name": b.name,
                    "address": b.address,
                    "rating": b.rating,
                    "phone": b.phone,
                    "website": b.website,
                }
                for b in chinese_result.businesses
                if "chinatown" not in b.name.lower()
            ],
        },
    }
    # Append collected knowledge to known_facts.md
    known_facts_path = os.path.join(
        os.path.dirname(__file__), "known_facts.md"
    )
    with open(known_facts_path, "a", encoding="utf-8") as f:
        f.write("\n\n## Round 1 — collected 2026-03-22\n\n```json\n")
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