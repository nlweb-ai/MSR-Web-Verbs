import os
import sys
import json
import re
# Add verbs directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "verbs"))
from maps_google_com__directions.maps_directions import get_maps_directions, MapsDirectionsRequest
# Origin: Red Roof Inn (Shuo's Mon–Tue hotel, used as reference for dealership proximity)
ORIGIN = "212 W Anthony Dr, Champaign, IL 61821"
# All 5 candidate dealerships from task-0003 "Still Needs Decision" table
DEALERSHIPS = [
    {"name": "Sam Leman Chevrolet",      "address": "440 Anthony Dr, Champaign, IL 61822"},
    {"name": "Sam Leman CDJR",           "address": "1906 Moreland Blvd, Champaign, IL 61822"},
    {"name": "Autotown",                 "address": "1200 W Bloomington Rd, Champaign, IL 61821"},
    {"name": "Champaign CDJR",           "address": "1906 Moreland Blvd, Champaign, IL 61822"},
    {"name": "Euro Motors",              "address": "50 E Springfield Ave, Champaign, IL 61820"},
]
def _parse_distance_miles(distance_str: str) -> float:
    """Convert a distance string like '2.5 miles', '1.1 mi', '3.2 km' to miles (float).
    Returns a large sentinel (9999) if unparseable so it sorts last."""
    if not distance_str:
        return 9999.0
    m = re.search(r"([\d.]+)\s*(miles?|mi\b|km|kilometers?)", distance_str, re.IGNORECASE)
    if not m:
        return 9999.0
    value = float(m.group(1))
    unit = m.group(2).lower()
    if "km" in unit or "kilo" in unit:
        value *= 0.621371  # convert km → miles
    return value
def automate(page):
    # Query Google Maps for driving distance from Red Roof Inn to each dealership
    directions_results = []
    for dealer in DEALERSHIPS:
        req = MapsDirectionsRequest(
            origin=ORIGIN,
            destination=dealer["address"],
        )
        res = get_maps_directions(page, req)
        dist_miles = _parse_distance_miles(res.distance)
        directions_results.append({
            "name":         dealer["name"],
            "address":      dealer["address"],
            "drive_time":   res.time,
            "distance_raw": res.distance,
            "distance_mi":  dist_miles,
        })
    # Sort ascending by distance; keep the 3 closest
    directions_results.sort(key=lambda d: d["distance_mi"])
    top3 = directions_results[:3]
    excluded = directions_results[3:]
    result = {
        "round": 3,
        "date": "2026-03-25",
        "dealership_distance_selection": {
            "note": (
                "Driving distances from Red Roof Inn (212 W Anthony Dr, Champaign) to each "
                "candidate dealership. The 3 closest are kept for Shuo's Sun–Tue visit plan."
            ),
            "origin": ORIGIN,
            "all_distances": directions_results,
            "top3_closest": [
                {
                    "name":         d["name"],
                    "address":      d["address"],
                    "drive_time":   d["drive_time"],
                    "distance":     d["distance_raw"],
                }
                for d in top3
            ],
            "excluded": [
                {
                    "name":    d["name"],
                    "address": d["address"],
                    "distance": d["distance_raw"],
                    "reason": "farther than top 3",
                }
                for d in excluded
            ],
        }
    }
    # Append the collected facts to known_facts.md
    facts_path = os.path.join(os.path.dirname(__file__), "known_facts.md")
    with open(facts_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n## Round 3 — Collected Facts ({result['date']})\n\n")
        f.write("```json\n")
        f.write(json.dumps(result, indent=2, ensure_ascii=False))
        f.write("\n```\n")
    return result