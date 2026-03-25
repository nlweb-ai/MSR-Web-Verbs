import os
import sys
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "verbs"))
from maps_google_com__createList.maps_createList import create_saved_list, CreateListRequest
def automate(page):
    # Today is 2026-03-25. Trip dates are Mar 28-31.
    # Task-0004 specifies 4 Google Maps lists for Shuo, one per day.
    # Each list groups places Shuo will visit that day to enable easy navigation.
    lists = [
        CreateListRequest(
            list_name="Shuo Mar 28 (Sat)",
            places=[
                # Arrival day: shared activities with Ashley
                "Papa Del's Pizza Factory, 1201 S Neil St, Champaign",       # Saturday lunch
                "University of Illinois LAR, 1005 S Lincoln Ave, Urbana",    # campus photo spot
                "U of I System Admin Bldg, 506 S Wright St, Urbana",         # campus photo spot
                "Illini Union, 1401 W Green St, Urbana",                     # campus photo spot
                "Main Quad, 607 S Mathews Ave, Urbana",                      # campus photo spot
                "Round Barns, 1201 St Marys Rd, Urbana",                     # campus photo spot
                "Writer's Room, 210 S Race St, Urbana",                      # Saturday dinner
                "La Quinta Inn Champaign, 1900 Center Dr, Champaign",        # Saturday night hotel
            ]
        ),
        CreateListRequest(
            list_name="Shuo Mar 29 (Sun)",
            places=[
                # Shuo checks in to Red Roof Inn, visits dealerships, housing, and dinner
                "Red Roof Inn Champaign, 212 W Anthony Dr, Champaign",        # Shuo's hotel Sun-Tue
                "Sam Leman Chevrolet, 440 Anthony Dr, Champaign",             # dealership ~2 min away
                "Autotown, 1200 W Bloomington Rd, Champaign",                 # dealership ~4 min / 1.7 mi
                "Euro Motors, 50 E Springfield Ave, Champaign",               # dealership ~7 min / 2.1 mi
                "Orchard Downs, 1801 Orchard Pl, Urbana",                     # UIUC-operated housing tour
                "Chinatown Buffet, 713 W Marketview Dr, Champaign",           # confirmed dinner
            ]
        ),
        CreateListRequest(
            list_name="Shuo Mar 30 (Mon)",
            places=[
                # Full day of housing tours + backup Chinese restaurants
                "Red Roof Inn Champaign, 212 W Anthony Dr, Champaign",
                "UIUC Family & Graduate Housing Office, 1841 Orchard Pl, Urbana",  # UIUC-operated housing
                "Hub on Campus, 812 S 6th St, Champaign",                          # private housing option
                "Campus Circle Urbana, 1010 W University Ave, Urbana",             # private housing option
                "Latitude Apartments, 608 E University Ave, Champaign",            # private housing option
                "Golden Harbor, 505 S Neil St, Champaign",                         # backup Chinese dinner
                "Rainbow Garden, 1402 S Neil St, Champaign",                       # backup Chinese option
                "Sunny China Buffet, 1703 Philo Rd, Urbana",                       # backup Chinese option
                "Peking Garden, 206 N Randolph St, Champaign",                     # backup Chinese option
            ]
        ),
        CreateListRequest(
            list_name="Shuo Mar 31 (Tue)",
            places=[
                # Drive north to Rosemont; return rental at ORD; check in to Sonesta
                "Red Roof Inn Champaign, 212 W Anthony Dr, Champaign",             # check-out location
                "Chicago O'Hare International Airport, Chicago, IL",               # return Avis rental
                "Sonesta Chicago O'Hare Airport, 10233 W Higgins Rd, Rosemont",   # overnight hotel
            ]
        ),
    ]
    results = []
    for req in lists:
        res = create_saved_list(page, req)
        results.append({
            "list_name": res.list_name,
            "places_added": res.places_added,
            "success": res.success,
        })
    result = {
        "round": 4,
        "date": "2026-03-25",
        "action": "Create Google Maps saved lists for Shuo (one per day Mar 28-31)",
        "lists_created": results,
    }
    # Append collected facts to known_facts.md
    facts_path = os.path.join(os.path.dirname(__file__), "tasks", "2026-03-19", "known_facts.md")
    with open(facts_path, "a", encoding="utf-8") as f:
        f.write("\n\n## Round 4 — Collected Facts (2026-03-25)\n\n")
        f.write("```json\n")
        f.write(json.dumps(result, indent=2, ensure_ascii=False))
        f.write("\n```\n")
    return result