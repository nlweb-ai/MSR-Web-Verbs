import os
import sys
import json
# Add verbs to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "verbs"))
from uber_com.uber_search import search_uber_rides, UberRideSearchRequest
def automate(page):
    # Task: Get Uber prices from Microsoft Building 99 (Redmond, WA) to SeaTac Airport departures.
    # Microsoft Building 99 is a well-known Microsoft campus building in Redmond, WA.
    # The destination is the Seattle-Tacoma International Airport Departures terminal.
    request = UberRideSearchRequest(
        pickup="Microsoft Building 99, 14820 NE 36th St, Redmond, WA 98052",
        dropoff="Seattle-Tacoma International Airport Departures, Seattle, WA 98188",
        max_results=10,
    )
    result = search_uber_rides(page, request)
    # Collect ride estimates into a structured dict
    estimates = [
        {"ride_type": e.ride_type, "price_range": e.price_range}
        for e in result.estimates
    ]
    output = {
        "pickup": result.pickup,
        "dropoff": result.dropoff,
        "estimates": estimates,
    }
    # Append findings to known_facts.md
    facts_path = os.path.join(os.path.dirname(__file__), "known_facts.md")
    with open(facts_path, "a", encoding="utf-8") as f:
        f.write("## Uber Prices: Microsoft Building 99 → SeaTac Departures\n\n")
        f.write(f"**Pickup:** {output['pickup']}\n\n")
        f.write(f"**Dropoff:** {output['dropoff']}\n\n")
        f.write("**Ride Estimates:**\n\n")
        for e in estimates:
            f.write(f"- {e['ride_type']}: {e['price_range']}\n")
        f.write("\n")
        f.write("```json\n")
        f.write(json.dumps(output, indent=2, ensure_ascii=False))
        f.write("\n```\n\n")
    return output