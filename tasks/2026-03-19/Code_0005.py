import os
import sys
import json
# Add verbs directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "verbs"))
from maps_google_com__nearby.maps_nearby import search_nearby, NearbySearchRequest
from maps_google_com__createList.maps_createList import create_saved_list, CreateListRequest
def automate(page):
    # ------------------------------------------------------------------
    # Refinement strategy for task-0005:
    # The only new ask is "add a dim sum place into this itinerary."
    # Champaign/Urbana is a college town; dedicated dim sum spots may be
    # scarce, so we search broadly for "dim sum" and pick the best result.
    # The natural insertion point is Mar 30 (Mon) — Shuo's free day with
    # multiple backup Chinese options already listed.  We add the dim sum
    # place to the "Shuo Mar 30 (Mon)" Google Maps list alongside the
    # existing Chinese restaurants so Shuo can choose on the day.
    # ------------------------------------------------------------------
    # Step 1: Search for dim sum restaurants near Champaign, IL
    dim_sum_search = search_nearby(page, NearbySearchRequest(
        query="dim sum restaurant",
        location="Champaign, IL",
        max_results=5
    ))
    businesses = dim_sum_search.businesses
    # Step 2: Recommend the highest-rated dim sum place
    # If no numeric rating is available, fall back to the first result.
    recommended = None
    best_rating = -1.0
    for b in businesses:
        try:
            r = float(b.rating)
            if r > best_rating:
                best_rating = r
                recommended = b
        except (ValueError, TypeError):
            pass
    if recommended is None and businesses:
        recommended = businesses[0]
    # Step 3: Update "Shuo Mar 30 (Mon)" Google Maps list to include the
    # dim sum place.  All existing Mar 30 places are re-added so the list
    # stays complete.
    mar30_base_places = [
        "Red Roof Inn Champaign",
        "UIUC Family & Graduate Housing Office",
        "Hub on Campus Champaign - Daniel",
        "Campus Circle Urbana",
        "Latitude Apartments",
        "Golden Harbor Authentic Chinese Cuisine",
        "Rainbow Garden",
        "Sunny China Buffet",
        "Peking Garden Restaurant",
    ]
    if recommended:
        # Insert dim sum as the first meal option so it's prominent
        mar30_base_places.insert(5, recommended.name)
    list_result = create_saved_list(page, CreateListRequest(
        list_name="Shuo Mar 30 (Mon)",
        places=mar30_base_places
    ))
    # Step 4: Build result dict capturing all newly-obtained knowledge
    result = {
        "round": 5,
        "date": "2026-03-31",
        "additional_ask": "Add a dim sum place to the itinerary",
        "dim_sum_search": {
            "query": dim_sum_search.query,
            "location": dim_sum_search.location,
            "all_results": [
                {
                    "name": b.name,
                    "address": b.address,
                    "rating": b.rating,
                    "phone": b.phone,
                    "website": b.website
                }
                for b in businesses
            ]
        },
        "recommended_dim_sum": {
            "name": recommended.name if recommended else None,
            "address": recommended.address if recommended else None,
            "rating": recommended.rating if recommended else None,
            "phone": recommended.phone if recommended else None,
            "website": recommended.website if recommended else None,
            "itinerary_slot": "Shuo Mon Mar 30 — dim sum meal option",
            "note": (
                "Best-rated dim sum option found in Champaign/Urbana area. "
                "Added as primary Chinese meal option for Mar 30. "
                "Backup Chinese options (Golden Harbor, Rainbow Garden, "
                "Sunny China Buffet, Peking Garden) remain available on the same day."
            )
        },
        "google_maps_list_update": {
            "list_name": list_result.list_name,
            "places_added": list_result.places_added,
            "success": list_result.success
        }
    }
    # Step 5: Append the result to known_facts.md
    known_facts_path = os.path.join(os.path.dirname(__file__), "known_facts.md")
    with open(known_facts_path, "a", encoding="utf-8") as f:
        f.write("\n\n## Round 5 — Collected Facts (2026-03-31)\n\n")
        f.write("```json\n")
        f.write(json.dumps(result, indent=2, ensure_ascii=False))
        f.write("\n```\n")
    return result