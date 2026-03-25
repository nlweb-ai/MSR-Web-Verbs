import os
import sys
import json
# Add verbs to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "verbs"))
from maps_google_com__nearby.maps_nearby import search_nearby, NearbySearchRequest
def automate(page):
    # Today: March 24, 2026 (Tuesday). "Next week" = Mar 28 – Apr 1, 2026.
    #
    # Concrete schedule:
    #   Mar 28 (Sat): Shuo & Ashley arrive Champaign (~mid-morning via rental car from ORD).
    #                 Lunch together + Dinner together.
    #                 Ashley likes Papa Del's for ONE meal → assign Papa Del's to DINNER
    #                 (Papa Del's opens at 5 PM; dinner makes more sense after a travel day).
    #                 Need a Saturday LUNCH recommendation near UIUC campus.
    #   Mar 29–31 (Sun–Tue): Ashley at UIUC department events.
    #                 Shuo: car dealerships, university housing, campus landmarks, Chinese food.
    #                 ONE meal at Chinatown Buffet; find backup Chinese options too.
    champaign = "Champaign, IL"
    uiuc = "University of Illinois Urbana-Champaign, Champaign, IL"
    # 1. Confirm Papa Del's details for Saturday dinner
    papas_result = search_nearby(page, NearbySearchRequest(
        query="Papa Del's Pizza",
        location=champaign,
        max_results=1
    ))
    # 2. Saturday lunch options near UIUC campus (not Papa Del's — that slot is dinner)
    lunch_result = search_nearby(page, NearbySearchRequest(
        query="restaurant lunch near University of Illinois",
        location=uiuc,
        max_results=5
    ))
    # 3. Chinese restaurants — must include Chinatown Buffet; surface alternatives too
    chinese_result = search_nearby(page, NearbySearchRequest(
        query="Chinese restaurant buffet",
        location=champaign,
        max_results=5
    ))
    # 4. Car dealerships for Shuo to visit Sun–Tue
    dealers_result = search_nearby(page, NearbySearchRequest(
        query="car dealership",
        location=champaign,
        max_results=5
    ))
    # 5. University housing options to tour (apartment communities near UIUC)
    housing_result = search_nearby(page, NearbySearchRequest(
        query="university student housing apartment",
        location=uiuc,
        max_results=5
    ))
    # 6. UIUC campus landmark photo spots
    landmarks_result = search_nearby(page, NearbySearchRequest(
        query="UIUC campus landmark",
        location=uiuc,
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
    result = {
        "schedule_summary": {
            "mar28_saturday": (
                "Arrive Champaign morning. "
                "Lunch together (see saturday_lunch_options). "
                "Dinner at Papa Del's (Ashley's choice)."
            ),
            "mar29_31_sun_tue": (
                "Ashley at UIUC department events. "
                "Shuo visits car dealerships, university housing, campus landmarks, "
                "and Chinese restaurants (Chinatown Buffet for one meal)."
            ),
        },
        "saturday_dinner_papas_del": {
            "note": "Papa Del's assigned to Saturday DINNER. Ashley's preferred meal.",
            "details": to_list(papas_result),
        },
        "saturday_lunch_options": to_list(lunch_result),
        "chinese_restaurants": {
            "note": "Chinatown Buffet is the confirmed one-meal stop; others are backups.",
            "options": to_list(chinese_result),
        },
        "car_dealerships_to_visit": to_list(dealers_result),
        "university_housing_to_tour": to_list(housing_result),
        "campus_landmark_photo_spots": to_list(landmarks_result),
    }
    # Append findings to known_facts.md in the same task folder
    known_facts_path = os.path.join(os.path.dirname(__file__), "known_facts.md")
    with open(known_facts_path, "a", encoding="utf-8") as f:
        f.write("## Round 1 — Collected Facts (2026-03-24)\n\n")
        f.write("```json\n")
        f.write(json.dumps(result, indent=2, ensure_ascii=False))
        f.write("\n```\n\n")
    return result